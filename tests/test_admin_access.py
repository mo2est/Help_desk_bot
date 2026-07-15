"""AdminAccessMiddleware tests: admin passes through, non-admin is rejected."""
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.types import CallbackQuery, Message

from app.middlewares.admin_access import AdminAccessMiddleware

ADMIN_ID = 111
STRANGER_ID = 222


def _event(spec, user_id):
    event = Mock(spec=spec)
    event.from_user = Mock()
    event.from_user.id = user_id
    event.answer = AsyncMock()
    return event


def _data(admin_ids):
    return {"bot_data": {"admin_ids": admin_ids}}


@pytest.mark.asyncio
async def test_admin_message_passes_through():
    mw = AdminAccessMiddleware()
    handler = AsyncMock(return_value="handled")
    event = _event(Message, ADMIN_ID)

    result = await mw(handler, event, _data([ADMIN_ID]))

    assert result == "handled"
    handler.assert_awaited_once()
    event.answer.assert_not_awaited()


@pytest.mark.asyncio
async def test_stranger_message_rejected():
    mw = AdminAccessMiddleware()
    handler = AsyncMock()
    event = _event(Message, STRANGER_ID)

    result = await mw(handler, event, _data([ADMIN_ID]))

    assert result is None
    handler.assert_not_awaited()
    event.answer.assert_awaited_once_with("⛔️ У вас нет доступа к админ-панели.")


@pytest.mark.asyncio
async def test_stranger_callback_rejected_with_alert():
    mw = AdminAccessMiddleware()
    handler = AsyncMock()
    event = _event(CallbackQuery, STRANGER_ID)

    result = await mw(handler, event, _data([ADMIN_ID]))

    assert result is None
    handler.assert_not_awaited()
    event.answer.assert_awaited_once_with("⛔️ Нет доступа.", show_alert=True)


@pytest.mark.asyncio
async def test_empty_admin_list_rejects_everyone():
    mw = AdminAccessMiddleware()
    handler = AsyncMock()
    event = _event(Message, ADMIN_ID)

    result = await mw(handler, event, _data([]))

    assert result is None
    handler.assert_not_awaited()


@pytest.mark.asyncio
async def test_missing_bot_data_rejects():
    mw = AdminAccessMiddleware()
    handler = AsyncMock()
    event = _event(CallbackQuery, ADMIN_ID)

    result = await mw(handler, event, {})

    assert result is None
    handler.assert_not_awaited()
