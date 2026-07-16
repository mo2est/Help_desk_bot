"""Helpers for tracking FSM prompt messages with active inline keyboards.

Telegram keeps inline keyboards attached to old messages forever, so a
multi-step FSM dialog leaves a trail of live "Cancel" buttons behind it.
We remember the id of the last prompt message in FSM data and strip its
keyboard as soon as the dialog moves on (next step, retry, completion or
a fresh /start / /admin).
"""
import logging

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

logger = logging.getLogger(__name__)


async def remember_prompt(state: FSMContext, message: Message) -> None:
    """Store the message that currently carries an active inline keyboard."""
    await state.update_data(
        prompt_msg_id=message.message_id,
        prompt_chat_id=message.chat.id,
    )


async def release_prompt(bot: Bot, state: FSMContext) -> None:
    """Remove the inline keyboard from the previously stored prompt message.

    Edit errors are swallowed: the message may be deleted, too old to edit
    or already stripped of its keyboard.
    """
    data = await state.get_data()
    msg_id = data.get("prompt_msg_id")
    chat_id = data.get("prompt_chat_id")
    if not msg_id or not chat_id:
        return
    await state.update_data(prompt_msg_id=None, prompt_chat_id=None)
    try:
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id, reply_markup=None)
    except Exception:
        logger.debug("Could not remove keyboard from message %s in chat %s", msg_id, chat_id)
