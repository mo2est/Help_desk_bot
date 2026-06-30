import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from app.database import get_session_factory, init_db
from app.handlers import admin, client
from app.middlewares.db import DbSessionMiddleware
from app.middlewares.throttling import ThrottlingMiddleware
from app.seed import seed_database

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def parse_admin_ids(raw: str) -> list[int]:
    if not raw:
        return []
    return [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]


async def main() -> None:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is required")

    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./helpdesk.db")
    admin_ids = parse_admin_ids(os.getenv("ADMIN_IDS", ""))

    await init_db(database_url)

    session_factory = get_session_factory()
    async with session_factory() as session:
        await seed_database(session)

    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    bot_data = {"bot": bot, "admin_ids": admin_ids}

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.update.middleware(DbSessionMiddleware(session_factory))
    dp.message.middleware(ThrottlingMiddleware(rate_limit=1.0))

    dp["bot_data"] = bot_data

    dp.include_router(admin.router)
    dp.include_router(client.router)

    logger.info("Starting Help Desk Bot...")
    logger.info(f"Admin IDs: {admin_ids}")

    try:
        await dp.start_polling(bot, bot_data=bot_data)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
