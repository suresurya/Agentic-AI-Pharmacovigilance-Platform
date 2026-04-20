from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from app.models.narrative import Narrative
from app.models.entity import Entity
from app.schemas.narrative import NarrativeCreate, NarrativeResponse
from app.schemas.entity import EntityOut

router = APIRouter(prefix="/api/v1/narratives", tags=["narratives"])


@router.post("/", response_model=NarrativeResponse)
async def submit_narrative(payload: NarrativeCreate, background_tasks: BackgroundTasks):
    narrative = Narrative(
        source_text=payload.source_text,
        source_type=payload.source_type,
        customer_id=payload.customer_id,
        status="queued",
    )
    await narrative.insert()

    from app.services.pipeline_runner import run_pipeline
    background_tasks.add_task(run_pipeline, str(narrative.id), payload.source_text)
    return _to_narrative_response(narrative)


@router.get("/{narrative_id}/", response_model=NarrativeResponse)
async def get_narrative(narrative_id: str):
    narrative = await Narrative.get(narrative_id)
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return _to_narrative_response(narrative)


@router.get("/{narrative_id}/entities/", response_model=list[EntityOut])
async def get_narrative_entities(narrative_id: str):
    entities = await Entity.find(Entity.narrative_id == narrative_id).to_list()
    return [_to_entity_out(e) for e in entities]


@router.post("/batch/")
async def submit_batch(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    import csv, io
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    job_ids = []
    for row in reader:
        text = row.get("text", row.get("narrative", "")).strip()
        if not text:
            continue
        narrative = Narrative(source_text=text, source_type="csv_batch", status="queued")
        await narrative.insert()
        job_ids.append(str(narrative.id))
        from app.services.pipeline_runner import run_pipeline
        background_tasks.add_task(run_pipeline, str(narrative.id), text)
    return {"job_ids": job_ids, "count": len(job_ids)}


def _to_narrative_response(n: Narrative) -> NarrativeResponse:
    return NarrativeResponse(
        id=str(n.id),
        source_text=n.source_text,
        source_type=n.source_type,
        language_mix_ratio=n.language_mix_ratio,
        status=n.status,
        created_at=n.created_at,
    )


def _to_entity_out(e: Entity) -> EntityOut:
    return EntityOut(
        id=str(e.id),
        narrative_id=e.narrative_id,
        entity_text=e.entity_text,
        entity_type=e.entity_type,
        char_start=e.char_start,
        char_end=e.char_end,
        confidence=e.confidence,
        source_model=e.source_model,
    )
