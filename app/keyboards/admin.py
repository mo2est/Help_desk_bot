from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models import Category, Question, UserQuestion


def admin_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Категории", callback_data="admin:categories")
    builder.button(text="❓ Вопросы пользователей", callback_data="admin:user_questions")
    builder.adjust(1)
    return builder.as_markup()


def admin_categories_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=f"{cat.emoji} {cat.name}", callback_data=f"admin:cat:{cat.id}")
    builder.button(text="➕ Добавить категорию", callback_data="admin:add_category")
    builder.button(text="◀️ Назад", callback_data="admin:main")
    builder.adjust(1)
    return builder.as_markup()


def admin_category_detail_keyboard(category_id: int, questions: list[Question]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for q in questions:
        short = q.text[:30] + "..." if len(q.text) > 30 else q.text
        builder.button(text=f"❓ {short}", callback_data=f"admin:q:{q.id}")
    builder.button(text="➕ Добавить вопрос", callback_data=f"admin:add_q:{category_id}")
    builder.button(text="🗑 Удалить категорию", callback_data=f"admin:del_cat_confirm:{category_id}")
    builder.button(text="◀️ Назад", callback_data="admin:categories")
    builder.adjust(1)
    return builder.as_markup()


def admin_confirm_delete_category_keyboard(category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 Да, удалить", callback_data=f"admin:del_cat:{category_id}")
    builder.button(text="❌ Отмена", callback_data=f"admin:cat:{category_id}")
    builder.adjust(1)
    return builder.as_markup()


def admin_question_detail_keyboard(question_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 Удалить вопрос", callback_data=f"admin:del_q:{question_id}")
    builder.button(text="◀️ Назад", callback_data="admin:categories")
    builder.adjust(1)
    return builder.as_markup()


def admin_user_questions_keyboard(questions: list[UserQuestion]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for uq in questions:
        short = uq.question_text[:25] + "..." if len(uq.question_text) > 25 else uq.question_text
        builder.button(
            text=f"#{uq.id} {uq.first_name or 'Аноним'}: {short}",
            callback_data=f"admin:uq:{uq.id}",
        )
    builder.button(text="◀️ Назад", callback_data="admin:main")
    builder.adjust(1)
    return builder.as_markup()


def admin_uq_detail_keyboard(uq_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Отметить отвеченным", callback_data=f"admin:uq_done:{uq_id}")
    builder.button(text="◀️ Назад", callback_data="admin:user_questions")
    builder.adjust(1)
    return builder.as_markup()


def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="admin:main")
    return builder.as_markup()
