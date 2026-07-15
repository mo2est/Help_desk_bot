import html

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
    admin_confirm_delete_category_keyboard,
    admin_main_keyboard,
    admin_question_detail_keyboard,
    admin_uq_detail_keyboard,
    admin_user_questions_keyboard,
)
from app.middlewares.admin_access import AdminAccessMiddleware

router = Router()
router.message.middleware(AdminAccessMiddleware())
router.callback_query.middleware(AdminAccessMiddleware())


class AdminStates(StatesGroup):
    add_category_name = State()
    add_category_emoji = State()
    add_question_text = State()
    add_question_answer = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🔧 <b>Админ-панель</b>", reply_markup=admin_main_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin:main")
async def admin_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("🔧 <b>Админ-панель</b>", reply_markup=admin_main_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:categories")
async def admin_categories(callback: CallbackQuery, session: AsyncSession) -> None:
    categories = await services.faq.get_categories(session)
    await callback.message.edit_text(
        "📋 <b>Категории</b>\nВыберите категорию для управления:",
        reply_markup=admin_categories_keyboard(categories),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:cat:"))
async def admin_category_detail(callback: CallbackQuery, session: AsyncSession) -> None:
    category_id = int(callback.data.split(":")[2])
    category = await services.faq.get_category(session, category_id)
    if not category:
        await callback.answer("Категория не найдена.", show_alert=True)
        return
    text = f"{category.emoji} <b>{html.escape(category.name)}</b>\nВопросов: {len(category.questions)}"
    await callback.message.edit_text(
        text,
        reply_markup=admin_category_detail_keyboard(category_id, category.questions),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "admin:add_category")
async def admin_add_category_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.add_category_name)
    await callback.message.edit_text(
        "Введите название новой категории:",
        reply_markup=admin_cancel_keyboard(),
    )
    await callback.answer()


@router.message(AdminStates.add_category_name)
async def admin_add_category_name(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.strip():
        await message.answer("Пожалуйста, отправьте название текстом.", reply_markup=admin_cancel_keyboard())
        return
    await state.update_data(cat_name=message.text.strip())
    await state.set_state(AdminStates.add_category_emoji)
    await message.answer("Введите эмодзи для категории (например: 💇):", reply_markup=admin_cancel_keyboard())


@router.message(AdminStates.add_category_emoji)
async def admin_add_category_emoji(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.text:
        await message.answer("Пожалуйста, отправьте эмодзи текстом.", reply_markup=admin_cancel_keyboard())
        return
    data = await state.get_data()
    emoji = message.text.strip() or "📌"
    cat = await services.faq.create_category(session, name=data["cat_name"], emoji=emoji)
    await state.clear()
    await message.answer(
        f"✅ Категория <b>{cat.emoji} {html.escape(cat.name)}</b> создана!",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("admin:del_cat_confirm:"))
async def admin_delete_category_confirm(callback: CallbackQuery, session: AsyncSession) -> None:
    category_id = int(callback.data.split(":")[2])
    category = await services.faq.get_category(session, category_id)
    if not category:
        await callback.answer("Категория не найдена.", show_alert=True)
        return
    text = (
        f"⚠️ Удалить категорию {category.emoji} <b>{html.escape(category.name)}</b>?\n"
        f"Вместе с ней будут удалены все её вопросы ({len(category.questions)} шт.)."
    )
    await callback.message.edit_text(
        text,
        reply_markup=admin_confirm_delete_category_keyboard(category_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:del_cat:"))
async def admin_delete_category(callback: CallbackQuery, session: AsyncSession) -> None:
    category_id = int(callback.data.split(":")[2])
    ok = await services.faq.delete_category(session, category_id)
    if ok:
        await callback.message.edit_text("🗑 Категория удалена.", reply_markup=admin_main_keyboard())
        await callback.answer()
    else:
        await callback.answer("Категория не найдена.", show_alert=True)


@router.callback_query(F.data.startswith("admin:add_q:"))
async def admin_add_question_start(callback: CallbackQuery, state: FSMContext) -> None:
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
    if not message.text or not message.text.strip():
        await message.answer("Пожалуйста, отправьте текст вопроса.", reply_markup=admin_cancel_keyboard())
        return
    await state.update_data(q_text=message.text.strip())
    await state.set_state(AdminStates.add_question_answer)
    await message.answer("Введите ответ на вопрос:", reply_markup=admin_cancel_keyboard())


@router.message(AdminStates.add_question_answer)
async def admin_add_question_answer(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.text or not message.text.strip():
        await message.answer("Пожалуйста, отправьте текст ответа.", reply_markup=admin_cancel_keyboard())
        return
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
async def admin_question_detail(callback: CallbackQuery, session: AsyncSession) -> None:
    question_id = int(callback.data.split(":")[2])
    q = await services.faq.get_question(session, question_id)
    if not q:
        await callback.answer("Вопрос не найден.", show_alert=True)
        return
    text = f"❓ <b>{html.escape(q.text)}</b>\n\n💬 {html.escape(q.answer)}"
    await callback.message.edit_text(
        text,
        reply_markup=admin_question_detail_keyboard(question_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:del_q:"))
async def admin_delete_question(callback: CallbackQuery, session: AsyncSession) -> None:
    question_id = int(callback.data.split(":")[2])
    ok = await services.faq.delete_question(session, question_id)
    if ok:
        await callback.message.edit_text("🗑 Вопрос удалён.", reply_markup=admin_main_keyboard())
    else:
        await callback.answer("Вопрос не найден.", show_alert=True)
    await callback.answer()


@router.callback_query(F.data == "admin:user_questions")
async def admin_user_questions(callback: CallbackQuery, session: AsyncSession) -> None:
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
async def admin_uq_detail(callback: CallbackQuery, session: AsyncSession) -> None:
    uq_id = int(callback.data.split(":")[2])
    uq = await services.faq.get_user_question(session, uq_id)
    if not uq:
        await callback.answer("Вопрос не найден.", show_alert=True)
        return
    user_ref = f"@{uq.username}" if uq.username else uq.first_name or f"ID:{uq.user_id}"
    text = (
        f"📩 <b>Вопрос #{uq.id}</b>\n"
        f"От: {html.escape(user_ref)}\n"
        f"Дата: {uq.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"<i>{html.escape(uq.question_text)}</i>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=admin_uq_detail_keyboard(uq_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:uq_done:"))
async def admin_uq_mark_done(callback: CallbackQuery, session: AsyncSession) -> None:
    uq_id = int(callback.data.split(":")[2])
    ok = await services.faq.mark_answered(session, uq_id)
    if ok:
        await callback.message.edit_text("✅ Вопрос отмечен как отвеченный.", reply_markup=admin_main_keyboard())
        await callback.answer()
    else:
        await callback.answer("Вопрос не найден.", show_alert=True)
