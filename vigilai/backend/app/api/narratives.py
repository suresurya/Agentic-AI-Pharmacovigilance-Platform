import asyncio
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.narrative import Narrative
from app.schemas.narrative import NarrativeCreate, NarrativeResponse, NarrativeStatus
from app.schemas.entity import EntityOut
from app.models.entity import Entity

router = APIRouter(prefix="/api/v1/narratives", tags=["narratives"])


@router.post("/", response_model=NarrativeResponse)
async def submit_narrative(
    payload: NarrativeCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    narrative = Narrative(
        source_text=payload.source_text,
        source_type=payload.source_type,
        customer_id=payload.customer_id,
        status="queued",
    )
    db.add(narrative)
    await db.commit()
    await db.refresh(narrative)

    from app.services.pipeline_runner import run_pipeline
    background_tasks.add_task(run_pipeline, str(narrative.id), payload.source_text)

    return narrative


@router.get("/{narrative_id}/", response_model=NarrativeResponse)
async def get_narrative(narrative_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Narrative).where(Narrative.id == narrative_id))
    narrative = result.scalar_one_or_none()
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return narrative


@router.get("/{narrative_id}/entities/", response_model=list[EntityOut])
async def get_narrative_entities(narrative_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Entity).where(Entity.narrative_id == narrative_id))
    return result.scalars().all()


@router.post("/batch/")
async def submit_batch(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    import csv
    import io
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    job_ids = []
    for row in reader:
        source_text = row.get("text", row.get("narrative", "")).strip()
        if not source_text:
            continue
        narrative = Narrative(source_text=source_text, source_type="csv_batch", status="queued")
        db.add(narrative)
        await db.flush()
        job_ids.append(str(narrative.id))
        from app.services.pipeline_runner import run_pipeline
        background_tasks.add_task(run_pipeline, str(narrative.id), source_text)
    await db.commit()
    return {"job_ids": job_ids, "count": len(job_ids)}
