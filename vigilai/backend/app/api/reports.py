from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.adr_report import ADRReport
from app.models.officer_action import OfficerAction
from app.models.narrative import Narrative
from app.schemas.report import ReportOut, ReportReviewRequest

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/", response_model=list[ReportOut])
async def list_reports(
    status: str | None = None,
    drug: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(ADRReport).order_by(ADRReport.created_at.desc()).offset(skip).limit(limit)
    if status:
        query = query.where(ADRReport.officer_status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/analytics/")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count(ADRReport.id)))
    pending = await db.scalar(select(func.count(ADRReport.id)).where(ADRReport.officer_status == "pending"))
    approved = await db.scalar(select(func.count(ADRReport.id)).where(ADRReport.officer_status == "approved"))
    rejected = await db.scalar(select(func.count(ADRReport.id)).where(ADRReport.officer_status == "rejected"))
    causes_adr = await db.scalar(select(func.count(ADRReport.id)).where(ADRReport.relation_type == "Causes-ADR"))
    possible_adr = await db.scalar(select(func.count(ADRReport.id)).where(ADRReport.relation_type == "Possible-ADR"))
    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "causes_adr": causes_adr,
        "possible_adr": possible_adr,
    }


@router.get("/{report_id}/", response_model=ReportOut)
async def get_report(report_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ADRReport).where(ADRReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.patch("/{report_id}/review/", response_model=ReportOut)
async def review_report(
    report_id: UUID,
    payload: ReportReviewRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ADRReport).where(ADRReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    original = {
        "officer_status": report.officer_status,
        "normalized_term": report.normalized_term,
        "whoart_code": report.whoart_code,
        "relation_type": report.relation_type,
    }
    corrected = {}

    if payload.action == "approve":
        report.officer_status = "approved"
        corrected["officer_status"] = "approved"
    elif payload.action == "reject":
        report.officer_status = "rejected"
        corrected["officer_status"] = "rejected"
    elif payload.action == "modify_term":
        report.officer_status = "modified"
        if payload.corrected_term:
            report.normalized_term = payload.corrected_term
            corrected["normalized_term"] = payload.corrected_term
        if payload.corrected_whoart_code:
            report.whoart_code = payload.corrected_whoart_code
            corrected["whoart_code"] = payload.corrected_whoart_code
    elif payload.action == "modify_relation":
        report.officer_status = "modified"
        if payload.corrected_relation:
            report.relation_type = payload.corrected_relation
            corrected["relation_type"] = payload.corrected_relation

    if payload.notes:
        report.officer_notes = payload.notes

    action = OfficerAction(
        report_id=report_id,
        action_type=payload.action,
        original_value=original,
        corrected_value=corrected,
        officer_id="demo-officer",
    )
    db.add(action)
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/{report_id}/export/")
async def export_report(report_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ADRReport).where(ADRReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    narrative_result = await db.execute(
        select(Narrative).where(Narrative.id == report.narrative_id)
    )
    narrative = narrative_result.scalar_one_or_none()

    export_data = {
        "report_id": str(report.id),
        "narrative_id": str(report.narrative_id),
        "source_text": narrative.source_text if narrative else None,
        "relation_type": report.relation_type,
        "confidence": report.confidence,
        "evidence": report.evidence,
        "normalized_term": report.normalized_term,
        "whoart_code": report.whoart_code,
        "officer_status": report.officer_status,
        "officer_notes": report.officer_notes,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }
    return JSONResponse(content=export_data)
