from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models import Category, Question


def main_menu_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=f"{cat.emoji} {cat.name}",
            callback_data=f"cat:{cat.id}",
        )
    builder.button(text="✉️ Задать свой вопрос", callback_data="ask_question")
    builder.adjust(1)
    return builder.as_markup()


def questions_keyboard(questions: list[Question], category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for q in sorted(questions, key=lambda x: (x.order, x.id)):
        builder.button(text=q.text, callback_data=f"q:{q.id}")
    builder.button(text="◀️ Назад", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def answer_keyboard(category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад к вопросам", callback_data=f"cat:{category_id}")
    builder.button(text="🏠 Главное меню", callback_data="back_to_menu")
    builder.button(text="✉️ Задать свой вопрос", callback_data="ask_question")
    builder.adjust(1)
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="back_to_menu")
    return builder.as_markup()
