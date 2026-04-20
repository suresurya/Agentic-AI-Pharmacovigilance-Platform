"""Seed demo narratives and pre-processed reports. Run: python -m app.seeds.seed_demo"""
import asyncio, json, os, sys, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from app.database import AsyncSessionLocal, engine, Base
from app.models.narrative import Narrative
from app.models.adr_report import ADRReport
from sqlalchemy import text

DEMO_FILE = os.path.join(os.path.dirname(__file__), "../../../../data/demo/curated_narratives.json")


async def seed():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    if not os.path.exists(DEMO_FILE):
        print("Demo narratives file not found — skipping demo seed")
        return

    with open(DEMO_FILE) as f:
        narratives = json.load(f)

    async with AsyncSessionLocal() as db:
        for item in narratives:
            narrative = Narrative(
                id=uuid.UUID(item["id"]) if "id" in item else uuid.uuid4(),
                source_text=item["text"],
                source_type="manual",
                language_mix_ratio=item.get("language_mix_ratio", 0.5),
                status="pending_review",
            )
            db.add(narrative)
            await db.flush()

            for report_data in item.get("reports", []):
                report = ADRReport(
                    narrative_id=narrative.id,
                    relation_type=report_data["relation_type"],
                    confidence=report_data["confidence"],
                    evidence=report_data.get("evidence", {}),
                    normalized_term=report_data.get("normalized_term"),
                    whoart_code=report_data.get("whoart_code"),
                    officer_status="pending",
                )
                db.add(report)

        await db.commit()
    print(f"Seeded {len(narratives)} demo narratives")


if __name__ == "__main__":
    asyncio.run(seed())
