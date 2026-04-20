"""Seed WHO-ART terms into MongoDB. Run: python -m app.seeds.seed_whoart"""
import asyncio, csv, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from app.database import init_db
from app.models.whoart_term import WHOARTTerm

WHOART_CSV = os.path.join(os.path.dirname(__file__), "../../../../data/whoart/whoart_terms.csv")


async def seed():
    await init_db()
    await WHOARTTerm.delete_all()

    if os.path.exists(WHOART_CSV):
        with open(WHOART_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            batch = [
                WHOARTTerm(
                    code=row.get("code", "0000"),
                    term=row.get("term", ""),
                    system_organ_class=row.get("system_organ_class"),
                )
                for row in reader
            ]
        await WHOARTTerm.insert_many(batch)
        print(f"Seeded {len(batch)} WHO-ART terms from CSV")
    else:
        print("WHO-ART CSV not found — skipping")


if __name__ == "__main__":
    asyncio.run(seed())
