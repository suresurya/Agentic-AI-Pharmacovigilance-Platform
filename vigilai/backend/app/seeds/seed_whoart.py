"""
Seed WHO-ART terms into PostgreSQL.
Run: python -m app.seeds.seed_whoart
"""
import asyncio
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from sqlalchemy import text
from app.database import engine, AsyncSessionLocal, Base
from app.models.whoart_term import WHOARTTerm

WHOART_CSV = os.path.join(os.path.dirname(__file__), "../../../../data/whoart/whoart_terms.csv")


async def seed():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    if not os.path.exists(WHOART_CSV):
        print(f"WHO-ART CSV not found at {WHOART_CSV} — generating synthetic terms")
        await _seed_synthetic()
        return

    async with AsyncSessionLocal() as db:
        with open(WHOART_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                term = WHOARTTerm(
                    code=row.get("code", "0000"),
                    term=row.get("term", ""),
                    system_organ_class=row.get("system_organ_class", None),
                )
                batch.append(term)
                if len(batch) >= 100:
                    db.add_all(batch)
                    await db.flush()
                    batch = []
            if batch:
                db.add_all(batch)
            await db.commit()
    print("WHO-ART terms seeded from CSV")


async def _seed_synthetic():
    """Seed a representative subset of WHO-ART terms for demo purposes."""
    terms = [
        ("0001", "Nausea NOS", "Gastrointestinal"),
        ("0002", "Vomiting NOS", "Gastrointestinal"),
        ("0003", "Nausea and vomiting", "Gastrointestinal"),
        ("0004", "Diarrhoea NOS", "Gastrointestinal"),
        ("0005", "Abdominal pain NOS", "Gastrointestinal"),
        ("0006", "Constipation", "Gastrointestinal"),
        ("0007", "Dyspepsia", "Gastrointestinal"),
        ("0008", "Flatulence", "Gastrointestinal"),
        ("0009", "Gastric irritation", "Gastrointestinal"),
        ("0010", "Headache NOS", "Central & Peripheral Nervous System"),
        ("0011", "Dizziness NOS", "Central & Peripheral Nervous System"),
        ("0012", "Tremor NOS", "Central & Peripheral Nervous System"),
        ("0013", "Insomnia NOS", "Psychiatric"),
        ("0014", "Fatigue", "Body as a Whole"),
        ("0015", "Weakness NOS", "Body as a Whole"),
        ("0016", "Oedema NOS", "Body as a Whole"),
        ("0017", "Rash NOS", "Skin & Appendages"),
        ("0018", "Pruritus NOS", "Skin & Appendages"),
        ("0019", "Urticaria NOS", "Skin & Appendages"),
        ("0020", "Palpitation", "Cardiovascular"),
        ("0021", "Tachycardia NOS", "Cardiovascular"),
        ("0022", "Bradycardia NOS", "Cardiovascular"),
        ("0023", "Hypotension NOS", "Cardiovascular"),
        ("0024", "Hypertension NOS", "Cardiovascular"),
        ("0025", "Dyspnoea NOS", "Respiratory"),
        ("0026", "Cough", "Respiratory"),
        ("0027", "Myalgia NOS", "Musculo-Skeletal"),
        ("0028", "Arthralgia NOS", "Musculo-Skeletal"),
        ("0029", "Back pain", "Musculo-Skeletal"),
        ("0030", "Hyperglycaemia NOS", "Metabolic & Nutritional"),
        ("0031", "Hypoglycaemia NOS", "Metabolic & Nutritional"),
        ("0032", "Weight increase", "Metabolic & Nutritional"),
        ("0033", "Weight decrease", "Metabolic & Nutritional"),
        ("0034", "Anorexia", "Metabolic & Nutritional"),
        ("0035", "Anxiety NOS", "Psychiatric"),
        ("0036", "Depression NOS", "Psychiatric"),
        ("0037", "Somnolence", "Central & Peripheral Nervous System"),
        ("0038", "Confusion NOS", "Central & Peripheral Nervous System"),
        ("0039", "Peripheral neuropathy NOS", "Central & Peripheral Nervous System"),
        ("0040", "Visual disturbance NOS", "Special Senses"),
        ("0041", "Tinnitus NOS", "Special Senses"),
        ("0042", "Dry mouth", "Gastrointestinal"),
        ("0043", "Taste perversion", "Special Senses"),
        ("0044", "Flushing NOS", "Vascular"),
        ("0045", "Chest pain NOS", "Body as a Whole"),
        ("0046", "Fever NOS", "Body as a Whole"),
        ("0047", "Chills NOS", "Body as a Whole"),
        ("0048", "Alopecia NOS", "Skin & Appendages"),
        ("0049", "Sweating increased", "Body as a Whole"),
        ("0050", "Liver function abnormal", "Liver & Biliary"),
        ("0051", "Jaundice NOS", "Liver & Biliary"),
        ("0052", "Hepatitis NOS", "Liver & Biliary"),
        ("0053", "Renal failure NOS", "Urinary"),
        ("0054", "Urinary frequency", "Urinary"),
        ("0055", "Blood creatinine increased", "Urinary"),
        ("0056", "Anaemia NOS", "Red Blood Cell"),
        ("0057", "Thrombocytopenia NOS", "Platelet/Bleeding"),
        ("0058", "Leucopenia NOS", "White Cell & Resistance"),
        ("0059", "Photosensitivity reaction", "Skin & Appendages"),
        ("0060", "Angioedema NOS", "Immune"),
        ("0061", "Anaphylactic reaction", "Immune"),
        ("0062", "Hypersensitivity reaction NOS", "Immune"),
        ("0063", "Muscle cramps NOS", "Musculo-Skeletal"),
        ("0064", "Joint swelling", "Musculo-Skeletal"),
        ("0065", "Neck pain", "Musculo-Skeletal"),
        ("0066", "Syncope NOS", "Central & Peripheral Nervous System"),
        ("0067", "Vertigo NOS", "Central & Peripheral Nervous System"),
        ("0068", "Paraesthesia NOS", "Central & Peripheral Nervous System"),
        ("0069", "Concentration impaired", "Psychiatric"),
        ("0070", "Memory impairment", "Psychiatric"),
        ("0071", "Irritability", "Psychiatric"),
        ("0072", "Agitation", "Psychiatric"),
        ("0073", "Libido decreased", "Psychiatric"),
        ("0074", "Dry skin", "Skin & Appendages"),
        ("0075", "Acne NOS", "Skin & Appendages"),
        ("0076", "Erythema NOS", "Skin & Appendages"),
        ("0077", "Ecchymosis", "Skin & Appendages"),
        ("0078", "Epistaxis", "Respiratory"),
        ("0079", "Nasal congestion", "Respiratory"),
        ("0080", "Pharyngitis NOS", "Respiratory"),
        ("0081", "Bronchospasm NOS", "Respiratory"),
        ("0082", "Hypokalaemia", "Metabolic & Nutritional"),
        ("0083", "Hyponatraemia", "Metabolic & Nutritional"),
        ("0084", "Oedema peripheral", "Cardiovascular"),
        ("0085", "QT prolongation", "Cardiovascular"),
        ("0086", "Arrhythmia NOS", "Cardiovascular"),
        ("0087", "Hot flushes", "Vascular"),
        ("0088", "Raynaud's phenomenon", "Vascular"),
        ("0089", "Pancreatitis NOS", "Gastrointestinal"),
        ("0090", "Stomatitis NOS", "Gastrointestinal"),
        ("0091", "Dysuria NOS", "Urinary"),
        ("0092", "Haematuria NOS", "Urinary"),
        ("0093", "Proteinuria NOS", "Urinary"),
        ("0094", "Thyroid function abnormal", "Endocrine"),
        ("0095", "Hyperuricaemia", "Metabolic & Nutritional"),
        ("0096", "Oculomotor disturbance", "Special Senses"),
        ("0097", "Hearing loss NOS", "Special Senses"),
        ("0098", "Epistaxis", "Body as a Whole"),
        ("0099", "Drug ineffective", "Body as a Whole"),
        ("0100", "Injection site reaction NOS", "Body as a Whole"),
    ]

    async with AsyncSessionLocal() as db:
        for code, term, soc in terms:
            db.add(WHOARTTerm(code=code, term=term, system_organ_class=soc))
        await db.commit()
    print(f"Seeded {len(terms)} synthetic WHO-ART terms")


if __name__ == "__main__":
    asyncio.run(seed())
