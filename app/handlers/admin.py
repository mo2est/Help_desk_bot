from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.keyboards.admin import (
    admin_cancel_keyboard,
    admin_categories_keyboard,
    admin_category_detail_keyboard,
    admin_main_keyboard,
    admin_question_detail_keyboard,
    admin_uq_detail_keyboard,
    admin_user_questions_keyboard,
)

router = Router()


class AdminStates(StatesGroup):
    add_category_name = State()
    add_category_emoji = State()
    add_question_text = State()
    add_question_answer = State()


def _is_admin(bot_data: dict, user_id: int) -> bool:
    return user_id in bot_data.get("admin_ids", [])


@router.message(Command("admin"))
async def cmd_admin(message: Message, bot_data: dict, state: FSMContext) -> None:
    if not _is_admin(bot_data, message.from_user.id):
        await message.answer("⛔️ У вас нет доступа к админ-панели.")
        return
    await state.clear()
    await message.answer("🔧 <b>Админ-панель</b>", reply_markup=admin_main_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin:main")
async def admin_main(callback: CallbackQuery, bot_data: dict, state: FSMContext) -> None:
    if not _is_admin(bot_data, callback.from_user.id):
        await callback.answer("⛔️ Нет доступа.", show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text("🔧 <b>Админ-панель</b>", reply_markup=admin_main_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:categories")
async def admin_categories(callback: CallbackQuery, session: AsyncSession, bot_data: dict) -> None:
    if not _is_admin(bot_data, callback.from_user.id):
        await callback.answer("⛔️ Нет доступа.", show_alert=True)
        return
    categories = await services.faq.get_categories(session)
    await callback.message.edit_text(
        "📋 <b>Категории</b>\nВыберите категорию для управления:",
        reply_markup=admin_categories_keyboard(categories),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:cat:"))
async def admin_category_detail(callback: CallbackQuery, session: AsyncSession, bot_data: dict) -> None:
    if not _is_admin(bot_data, callback.from_user.id):
        await callback.answer("⛔️ Нет доступа.", show_alert=True)
        return
    category_id = int(callback.data.split(":")[2])
    category = await services.faq.get_category(session, category_id)
    if not category:
        await callback.answer("Категория не найдена.", show_alert=True)
        return
    text = f"{category.emoji} <b>{category.name}</b>\nВопросов: {len(category.questions)}"
    await callback.message.edit_text(
        text,
        reply_markup=admin_category_detail_keyboard(category_id, category.questions),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "admin:add_category")
async def admin_add_category_start(callback: CallbackQuery, bot_data: dict, state: FSMContext) -> None:
    if not _is_admin(bot_data, callback.from_user.id):
        await callback.answer("⛔️ Нет доступа.", show_alert=True)
        return
    await state.set_state(AdminStates.add_category_name)
    await callback.message.edit_text(
        "Введите название новой категории:",
        reply_markup=admin_cancel_keyboard(),
    )
    await callback.answer()


@router.message(AdminStates.add_category_name)
async def admin_add_category_name(message: Message, state: FSMContext) -> None:
    await state.update_data(cat_name=message.text.strip())
    await state.set_state(AdminStates.add_category_emoji)
    await message.answer("Введите эмодзи для категории (например: 💇):", reply_markup=admin_cancel_keyboard())


@router.message(AdminStates.add_category_emoji)
async def admin_add_category_emoji(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    emoji = message.text.strip() or "📌"
    cat = await services.faq.create_category(session, name=data["cat_name"], emoji=emoji)
    await state.clear()
    await message.answer(
        f"✅ Категория <b>{cat.emoji} {cat.name}</b> создана!",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("admin:del_cat:"))
async def admin_delete_category(callback: CallbackQuery, session: AsyncSession, bot_data: dict) -> None:
    if not _is_admin(bot_data, callback.from_user.id):
        await callback.answer("⛔️ Нет доступа.", show_alert=True)
        return
    category_id = int(callback.data.split(":")[2])
    ok = await services.faq.delete_category(session, category_id)
    if ok:
        await callback.message.edit_text("🗑 Категория удалена.", reply_markup=admin_main_keyboard())
    else:
        await callback.answer("Категория не найдена.", show_alert=True)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:add_q:"))
async def admin_add_question_start(callback: CallbackQuery, bot_data: dict, state: FSMContext) -> None:
    if not _is_admin(bot_data, callback.from_user.id):
        await callback.answer("⛔️ Нет доступа.", show_alert=True)
        return
    category_id = int(callback.data.split(":")[2])
    await state.update_data(category_id=category_id)
    await state.set_state(AdminStates.add_question_text)
    await callback.message.edit_text(
        "Введите текст вопроса:",
        reply_markup=admin_cancel_keyboard(),
    )
    await callback.answer()


@router.message(AdminStates.add_question_text)
async def admin_add_question_text(message: Message, state: FSMContext) -> None:
    await state.update_data(q_text=message.text.strip())
    await state.set_state(AdminStates.add_question_answer)
    await message.answer("Введите ответ на вопрос:", reply_markup=admin_cancel_keyboard())


@router.message(AdminStates.add_question_answer)
async def admin_add_question_answer(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    q = await services.faq.create_question(
        session,
        category_id=data["category_id"],
        text=data["q_text"],
        answer=message.text.strip(),
    )
    await state.clear()
    if q:
        await message.answer("✅ Вопрос добавлен!", reply_markup=admin_main_keyboard())
    else:
        await message.answer("❌ Ошибка: категория не найдена.", reply_markup=admin_main_keyboard())


@router.callback_query(F.data.startswith("admin:q:"))
async def admin_question_detail(callback: CallbackQuery, session: AsyncSession, bot_data: dict) -> None:
    if not _is_admin(bot_data, callback.from_user.id):
        await callback.answer("⛔️ Нет доступа.", show_alert=True)
        return
    question_id = int(callback.data.split(":")[2])
    q = await services.faq.get_question(session, question_id)
    if not q:
        await callback.answer("Вопрос не найден.", show_alert=True)
        return
    text = f"❓ <b>{q.text}</b>\n\n💬 {q.answer}"
    await callback.message.edit_text(
        text,
        reply_markup=admin_question_detail_keyboard(question_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:del_q:"))
async def admin_delete_question(callback: CallbackQuery, session: AsyncSession, bot_data: dict) -> None:
    if not _is_admin(bot_data, callback.from_user.id):
        await callback.answer("⛔️ Нет доступа.", show_alert=True)
        return
    question_id = int(callback.data.split(":")[2])
    ok = await services.faq.delete_question(session, question_id)
    if ok:
        await callback.message.edit_text("🗑 Вопрос удалён.", reply_markup=admin_main_keyboard())
    else:
        await callback.answer("Вопрос не найден.", show_alert=True)
    await callback.answer()


@router.callback_query(F.data == "admin:user_questions")
async def admin_user_questions(callback: CallbackQuery, session: AsyncSession, bot_data: dict) -> None:
    if not _is_admin(bot_data, callback.from_user.id):
        await callback.answer("⛔️ Нет доступа.", show_alert=True)
        return
    questions = await services.faq.get_unanswered_questions(session)
    if not questions:
        await callback.message.edit_text(
            "✅ Нет неотвеченных вопросов.",
            reply_markup=admin_main_keyboard(),
        )
    else:
        await callback.message.edit_text(
            f"❓ <b>Неотвеченные вопросы</b> ({len(questions)}):",
            reply_markup=admin_user_questions_keyboard(questions),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:uq:"))
async def admin_uq_detail(callback: CallbackQuery, session: AsyncSession, bot_data: dict) -> None:
    if not _is_admin(bot_data, callback.from_user.id):
        await callback.answer("⛔️ Нет доступа.", show_alert=True)
        return
    uq_id = int(callback.data.split(":")[2])
    from sqlalchemy import select
    from app.models import UserQuestion
    result = await session.execute(select(UserQuestion).where(UserQuestion.id == uq_id))
    uq = result.scalar_one_or_none()
    if not uq:
        await callback.answer("Вопрос не найден.", show_alert=True)
        return
    user_ref = f"@{uq.username}" if uq.username else uq.first_name or f"ID:{uq.user_id}"
    text = (
        f"📩 <b>Вопрос #{uq.id}</b>\n"
        f"От: {user_ref}\n"
        f"Дата: {uq.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"<i>{uq.question_text}</i>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=admin_uq_detail_keyboard(uq_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:uq_done:"))
async def admin_uq_mark_done(callback: CallbackQuery, session: AsyncSession, bot_data: dict) -> None:
    if not _is_admin(bot_data, callback.from_user.id):
        await callback.answer("⛔️ Нет доступа.", show_alert=True)
        return
    uq_id = int(callback.data.split(":")[2])
    await services.faq.mark_answered(session, uq_id)
    await callback.message.edit_text("✅ Вопрос отмечен как отвеченный.", reply_markup=admin_main_keyboard())
    await callback.answer()
