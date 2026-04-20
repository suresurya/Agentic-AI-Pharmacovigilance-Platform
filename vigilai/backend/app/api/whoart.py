from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.whoart_term import WHOARTTerm

router = APIRouter(prefix="/api/v1/whoart", tags=["whoart"])


@router.get("/search/")
async def search_whoart(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WHOARTTerm)
        .where(WHOARTTerm.term.ilike(f"%{q}%"))
        .limit(10)
    )
    terms = result.scalars().all()
    return [
        {"id": t.id, "code": t.code, "term": t.term, "system_organ_class": t.system_organ_class}
        for t in terms
    ]
