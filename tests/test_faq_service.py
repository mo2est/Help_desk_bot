"""Service-layer tests: FAQ CRUD, user questions, seed guard."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Base
from app.seed import seed_database
from app.services import faq


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


@pytest.mark.asyncio
async def test_category_crud(session):
    cat = await faq.create_category(session, name="Test", emoji="🧪")
    assert cat.id is not None

    categories = await faq.get_categories(session)
    assert len(categories) == 1
    assert categories[0].name == "Test"

    fetched = await faq.get_category(session, cat.id)
    assert fetched is not None
    assert fetched.emoji == "🧪"

    assert await faq.delete_category(session, cat.id) is True
    assert await faq.get_categories(session) == []


@pytest.mark.asyncio
async def test_delete_missing_category_returns_false(session):
    assert await faq.delete_category(session, 999) is False


@pytest.mark.asyncio
async def test_question_crud_and_category_validation(session):
    cat = await faq.create_category(session, name="Prices")

    q = await faq.create_question(session, category_id=cat.id, text="Cost?", answer="100")
    assert q is not None
    assert (await faq.get_question(session, q.id)).answer == "100"

    # creating a question for a nonexistent category must fail gracefully
    assert await faq.create_question(session, category_id=999, text="x", answer="y") is None

    assert await faq.delete_question(session, q.id) is True
    assert await faq.get_question(session, q.id) is None


@pytest.mark.asyncio
async def test_deleting_category_cascades_questions(session):
    cat = await faq.create_category(session, name="Tmp")
    q = await faq.create_question(session, category_id=cat.id, text="Q", answer="A")

    await faq.delete_category(session, cat.id)
    assert await faq.get_question(session, q.id) is None


@pytest.mark.asyncio
async def test_user_question_flow(session):
    uq = await faq.save_user_question(
        session, user_id=42, username="alice", first_name="Alice", question_text="Help?"
    )
    assert uq.id is not None
    assert uq.is_answered is False

    unanswered = await faq.get_unanswered_questions(session)
    assert [x.id for x in unanswered] == [uq.id]

    assert await faq.mark_answered(session, uq.id) is True
    assert await faq.get_unanswered_questions(session) == []

    # already answered / missing ids report failure honestly
    assert await faq.mark_answered(session, 999) is False

    fetched = await faq.get_user_question(session, uq.id)
    assert fetched is not None and fetched.is_answered is True


@pytest.mark.asyncio
async def test_seed_is_idempotent(session):
    await seed_database(session)
    first_count = len(await faq.get_categories(session))
    assert first_count > 0

    await seed_database(session)
    assert len(await faq.get_categories(session)) == first_count
