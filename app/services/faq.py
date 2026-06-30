from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Category, Question, UserQuestion


async def get_categories(session: AsyncSession) -> list[Category]:
    result = await session.execute(
        select(Category).order_by(Category.order, Category.id)
    )
    return list(result.scalars().all())


async def get_category(session: AsyncSession, category_id: int) -> Category | None:
    result = await session.execute(
        select(Category)
        .where(Category.id == category_id)
        .options(selectinload(Category.questions))
    )
    return result.scalar_one_or_none()


async def get_question(session: AsyncSession, question_id: int) -> Question | None:
    result = await session.execute(
        select(Question).where(Question.id == question_id)
    )
    return result.scalar_one_or_none()


async def save_user_question(
    session: AsyncSession,
    user_id: int,
    username: str | None,
    first_name: str | None,
    question_text: str,
) -> UserQuestion:
    uq = UserQuestion(
        user_id=user_id,
        username=username,
        first_name=first_name,
        question_text=question_text,
    )
    session.add(uq)
    await session.commit()
    await session.refresh(uq)
    return uq


async def get_unanswered_questions(session: AsyncSession) -> list[UserQuestion]:
    result = await session.execute(
        select(UserQuestion)
        .where(UserQuestion.is_answered == False)
        .order_by(UserQuestion.created_at.desc())
    )
    return list(result.scalars().all())


async def mark_answered(session: AsyncSession, question_id: int) -> None:
    result = await session.execute(
        select(UserQuestion).where(UserQuestion.id == question_id)
    )
    uq = result.scalar_one_or_none()
    if uq:
        uq.is_answered = True
        await session.commit()


# Admin CRUD

async def create_category(session: AsyncSession, name: str, emoji: str = "📌") -> Category:
    cat = Category(name=name, emoji=emoji)
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    return cat


async def delete_category(session: AsyncSession, category_id: int) -> bool:
    cat = await session.get(Category, category_id)
    if not cat:
        return False
    await session.delete(cat)
    await session.commit()
    return True


async def create_question(
    session: AsyncSession, category_id: int, text: str, answer: str
) -> Question | None:
    cat = await session.get(Category, category_id)
    if not cat:
        return None
    q = Question(category_id=category_id, text=text, answer=answer)
    session.add(q)
    await session.commit()
    await session.refresh(q)
    return q


async def delete_question(session: AsyncSession, question_id: int) -> bool:
    q = await session.get(Question, question_id)
    if not q:
        return False
    await session.delete(q)
    await session.commit()
    return True
