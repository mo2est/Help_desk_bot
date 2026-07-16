import html
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app import services
from app.keyboards.client import (
    answer_keyboard,
    cancel_keyboard,
    main_menu_keyboard,
    questions_keyboard,
)
from app.utils import release_prompt, remember_prompt

router = Router()
logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "👋 Добро пожаловать в Help Desk салона красоты <b>BeautyPro</b>!\n\n"
    "Выберите интересующую вас категорию или задайте свой вопрос:"
)


class AskQuestionState(StatesGroup):
    waiting_for_question = State()


async def send_main_menu(target: Message | CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await release_prompt(target.bot, state)
    await state.clear()
    categories = await services.faq.get_categories(session)
    kb = main_menu_keyboard(categories)
    if isinstance(target, Message):
        await target.answer(WELCOME_TEXT, reply_markup=kb, parse_mode="HTML")
    else:
        await target.message.edit_text(WELCOME_TEXT, reply_markup=kb, parse_mode="HTML")


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, state: FSMContext) -> None:
    await send_main_menu(message, session, state)


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await send_main_menu(callback, session, state)
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_category(callback: CallbackQuery, session: AsyncSession) -> None:
    category_id = int(callback.data.split(":")[1])
    category = await services.faq.get_category(session, category_id)
    if not category:
        await callback.answer("Категория не найдена.", show_alert=True)
        return

    text = f"{category.emoji} <b>{html.escape(category.name)}</b>\n\nВыберите вопрос:"
    kb = questions_keyboard(category.questions, category_id)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("q:"))
async def show_answer(callback: CallbackQuery, session: AsyncSession) -> None:
    question_id = int(callback.data.split(":")[1])
    question = await services.faq.get_question(session, question_id)
    if not question:
        await callback.answer("Вопрос не найден.", show_alert=True)
        return

    text = f"❓ <b>{html.escape(question.text)}</b>\n\n💬 {html.escape(question.answer)}"
    kb = answer_keyboard(question.category_id)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "ask_question")
async def ask_question_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AskQuestionState.waiting_for_question)
    await callback.message.edit_text(
        "✏️ Напишите ваш вопрос, и мы передадим его администратору:",
        reply_markup=cancel_keyboard(),
    )
    await remember_prompt(state, callback.message)
    await callback.answer()


@router.message(AskQuestionState.waiting_for_question)
async def ask_question_receive(
    message: Message, state: FSMContext, session: AsyncSession, bot_data: dict
) -> None:
    from aiogram import Bot

    question_text = message.text or ""
    if not question_text.strip():
        await release_prompt(message.bot, state)
        retry = await message.answer(
            "Пожалуйста, отправьте текстовое сообщение.", reply_markup=cancel_keyboard()
        )
        await remember_prompt(state, retry)
        return

    await release_prompt(message.bot, state)
    user = message.from_user
    uq = await services.faq.save_user_question(
        session,
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        question_text=question_text,
    )

    await message.answer(
        "✅ Ваш вопрос принят! Администратор свяжется с вами в ближайшее время.\n"
        "Введите /start чтобы вернуться в меню."
    )
    await state.clear()

    # Notify admins
    bot: Bot = bot_data["bot"]
    admin_ids: list[int] = bot_data["admin_ids"]
    if user.username:
        user_link = f"@{user.username}"
    else:
        user_link = f"<a href='tg://user?id={user.id}'>{html.escape(user.first_name or 'Пользователь')}</a>"
    admin_text = (
        f"📩 <b>Новый вопрос #{uq.id}</b>\n"
        f"От: {user_link}\n\n"
        f"<i>{html.escape(question_text)}</i>"
    )
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, admin_text, parse_mode="HTML")
        except Exception:
            logger.exception("Failed to notify admin %s about question #%s", admin_id, uq.id)
