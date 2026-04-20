from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.models.adr_report import ADRReport
from app.models.officer_action import OfficerAction
from app.models.narrative import Narrative
from app.schemas.report import ReportOut, ReportReviewRequest

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


def _to_out(r: ADRReport) -> ReportOut:
    return ReportOut(
        id=str(r.id),
        narrative_id=r.narrative_id,
        drug_entity_id=r.drug_entity_id,
        symptom_entity_id=r.symptom_entity_id,
        relation_type=r.relation_type,
        confidence=r.confidence,
        evidence=r.evidence,
        normalized_term=r.normalized_term,
        whoart_code=r.whoart_code,
        officer_status=r.officer_status,
        officer_notes=r.officer_notes,
        created_at=r.created_at,
    )


@router.get("/analytics/")
async def get_analytics():
    total = await ADRReport.count()
    pending = await ADRReport.find(ADRReport.officer_status == "pending").count()
    approved = await ADRReport.find(ADRReport.officer_status == "approved").count()
    rejected = await ADRReport.find(ADRReport.officer_status == "rejected").count()
    causes = await ADRReport.find(ADRReport.relation_type == "Causes-ADR").count()
    possible = await ADRReport.find(ADRReport.relation_type == "Possible-ADR").count()
    return {
        "total": total, "pending": pending, "approved": approved,
        "rejected": rejected, "causes_adr": causes, "possible_adr": possible,
    }


@router.get("/", response_model=list[ReportOut])
async def list_reports(status: str | None = None, skip: int = 0, limit: int = 50):
    query = ADRReport.find(ADRReport.officer_status == status) if status else ADRReport.find()
    reports = await query.skip(skip).limit(limit).sort(-ADRReport.created_at).to_list()
    return [_to_out(r) for r in reports]


@router.get("/{report_id}/", response_model=ReportOut)
async def get_report(report_id: str):
    report = await ADRReport.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return _to_out(report)


@router.patch("/{report_id}/review/", response_model=ReportOut)
async def review_report(report_id: str, payload: ReportReviewRequest):
    report = await ADRReport.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    original = {
        "officer_status": report.officer_status,
        "normalized_term": report.normalized_term,
        "whoart_code": report.whoart_code,
        "relation_type": report.relation_type,
    }
    corrected: dict = {}

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

    await report.save()
    await OfficerAction(
        report_id=report_id,
        action_type=payload.action,
        original_value=original,
        corrected_value=corrected,
        officer_id="demo-officer",
    ).insert()
    return _to_out(report)


@router.get("/{report_id}/export/")
async def export_report(report_id: str):
    report = await ADRReport.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    narrative = await Narrative.get(report.narrative_id)
    return JSONResponse({
        "report_id": str(report.id),
        "narrative_id": report.narrative_id,
        "source_text": narrative.source_text if narrative else None,
        "relation_type": report.relation_type,
        "confidence": report.confidence,
        "evidence": report.evidence,
        "normalized_term": report.normalized_term,
        "whoart_code": report.whoart_code,
        "officer_status": report.officer_status,
        "officer_notes": report.officer_notes,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    })
