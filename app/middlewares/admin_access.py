from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class AdminAccessMiddleware(BaseMiddleware):
    """Router-scoped guard: rejects events from users not listed in bot_data['admin_ids'].

    Registered as inner middleware on the admin router, so it runs only for
    updates that already matched an admin handler - one check instead of a
    copy-pasted guard in every handler, and FSM message handlers are covered too.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        bot_data: dict = data.get("bot_data") or {}
        user = getattr(event, "from_user", None)
        if user is None or user.id not in bot_data.get("admin_ids", []):
            if isinstance(event, CallbackQuery):
                await event.answer("⛔️ Нет доступа.", show_alert=True)
            elif isinstance(event, Message):
                await event.answer("⛔️ У вас нет доступа к админ-панели.")
            return None
        return await handler(event, data)
