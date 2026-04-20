"""Seed demo narratives and pre-processed reports. Run: python -m app.seeds.seed_demo"""
import asyncio, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from app.database import init_db
from app.models.narrative import Narrative
from app.models.adr_report import ADRReport

DEMO_FILE = os.path.join(os.path.dirname(__file__), "../../../../data/demo/curated_narratives.json")


async def seed():
    await init_db()

    if not os.path.exists(DEMO_FILE):
        print("Demo file not found — skipping")
        return

    # Clear existing demo data
    await Narrative.find(Narrative.source_type == "manual").delete()
    await ADRReport.find().delete()

    with open(DEMO_FILE) as f:
        items = json.load(f)

    count = 0
    for item in items:
        narrative = Narrative(
            source_text=item["text"],
            source_type="manual",
            language_mix_ratio=item.get("language_mix_ratio", 0.5),
            status="pending_review" if item.get("reports") else "done",
        )
        await narrative.insert()

        for r in item.get("reports", []):
            await ADRReport(
                narrative_id=str(narrative.id),
                relation_type=r["relation_type"],
                confidence=r["confidence"],
                evidence=r.get("evidence", {}),
                normalized_term=r.get("normalized_term"),
                whoart_code=r.get("whoart_code"),
                officer_status="pending",
            ).insert()
        count += 1

    print(f"Seeded {count} demo narratives")


if __name__ == "__main__":
    asyncio.run(seed())
