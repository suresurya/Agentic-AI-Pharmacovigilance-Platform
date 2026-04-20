from fastapi import APIRouter, HTTPException
from app.models.adr_report import ADRReport
from app.schemas.hitl import HITLResolveRequest

router = APIRouter(prefix="/api/v1/reports", tags=["hitl"])


@router.post("/{report_id}/resolve-hitl/")
async def resolve_hitl(report_id: str, payload: HITLResolveRequest):
    report = await ADRReport.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.normalized_term = payload.selected_term
    report.whoart_code = payload.selected_code
    await report.save()

    from app.services.pipeline_runner import resume_pipeline
    await resume_pipeline(
        report.narrative_id,
        report_id,
        {"selected_term": payload.selected_term, "selected_code": payload.selected_code},
    )
    return {"status": "resumed", "report_id": report_id}
