from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.adr_report import ADRReport
from app.schemas.hitl import HITLResolveRequest

router = APIRouter(prefix="/api/v1/reports", tags=["hitl"])


@router.post("/{report_id}/resolve-hitl/")
async def resolve_hitl(
    report_id: UUID,
    payload: HITLResolveRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ADRReport).where(ADRReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.normalized_term = payload.selected_term
    report.whoart_code = payload.selected_code
    await db.commit()

    from app.services.pipeline_runner import resume_pipeline
    await resume_pipeline(
        str(report.narrative_id),
        str(report_id),
        {"selected_term": payload.selected_term, "selected_code": payload.selected_code},
    )

    return {"status": "resumed", "report_id": str(report_id)}
