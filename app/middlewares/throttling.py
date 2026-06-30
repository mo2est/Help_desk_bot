import time
from collections import defaultdict
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

RATE_LIMIT = 1.0  # seconds between messages per user


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = RATE_LIMIT) -> None:
        self.rate_limit = rate_limit
        self._last_called: dict[int, float] = defaultdict(float)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            now = time.monotonic()
            delta = now - self._last_called[user_id]
            if delta < self.rate_limit:
                await event.answer(
                    f"⏳ Пожалуйста, не торопитесь. Подождите {self.rate_limit - delta:.1f} сек."
                )
                return
            self._last_called[user_id] = now
        return await handler(event, data)
