import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

RATE_LIMIT = 1.0  # seconds between messages per user
CLEANUP_THRESHOLD = 10_000  # max tracked users before stale entries are purged


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = RATE_LIMIT) -> None:
        self.rate_limit = rate_limit
        self._last_called: dict[int, float] = {}
        self._warned: set[int] = set()

    def _cleanup(self, now: float) -> None:
        stale = [uid for uid, ts in self._last_called.items() if now - ts > self.rate_limit]
        for uid in stale:
            self._last_called.pop(uid, None)
            self._warned.discard(uid)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            now = time.monotonic()
            if len(self._last_called) > CLEANUP_THRESHOLD:
                self._cleanup(now)
            delta = now - self._last_called.get(user_id, 0.0)
            if delta < self.rate_limit:
                # Warn once per flood episode, then drop silently so the bot
                # does not mirror the flood with its own outgoing messages.
                if user_id not in self._warned:
                    self._warned.add(user_id)
                    await event.answer("⏳ Пожалуйста, не торопитесь.")
                return
            self._last_called[user_id] = now
            self._warned.discard(user_id)
        return await handler(event, data)
