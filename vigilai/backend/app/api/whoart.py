import re
from fastapi import APIRouter, Query
from app.models.whoart_term import WHOARTTerm

router = APIRouter(prefix="/api/v1/whoart", tags=["whoart"])


@router.get("/search/")
async def search_whoart(q: str = Query(..., min_length=2)):
    pattern = re.compile(q, re.IGNORECASE)
    terms = await WHOARTTerm.find({"term": {"$regex": q, "$options": "i"}}).limit(10).to_list()
    return [{"id": str(t.id), "code": t.code, "term": t.term, "system_organ_class": t.system_organ_class} for t in terms]
