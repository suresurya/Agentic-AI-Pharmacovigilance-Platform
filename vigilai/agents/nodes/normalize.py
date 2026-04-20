import os
import asyncio
from agents.state import AgentState

HITL_THRESHOLD = 0.82


def _get_top_whoart_candidates(symptom_text: str, top_k: int = 3) -> list[dict]:
    """Query pgvector for top-k WHO-ART candidates by cosine similarity."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        import numpy as np
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
        embedding = model.encode(symptom_text).tolist()

        db_url = os.environ.get("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            SELECT code, term, system_organ_class,
                   1 - (embedding <=> %s::vector) AS score
            FROM whoart_terms
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (embedding, embedding, top_k),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [
            {
                "rank": i + 1,
                "code": row["code"],
                "term": row["term"],
                "system_organ_class": row["system_organ_class"],
                "score": round(float(row["score"]), 4),
            }
            for i, row in enumerate(rows)
        ]
    except Exception as e:
        print(f"pgvector search failed: {e} — using text fallback")
        return _text_fallback(symptom_text, top_k)


def _text_fallback(symptom_text: str, top_k: int = 3) -> list[dict]:
    """Simple text-match fallback when embeddings unavailable."""
    from difflib import SequenceMatcher

    WHOART_SAMPLE = [
        ("0001", "Nausea NOS", "Gastrointestinal"),
        ("0002", "Vomiting NOS", "Gastrointestinal"),
        ("0010", "Headache NOS", "Central & Peripheral Nervous System"),
        ("0011", "Dizziness NOS", "Central & Peripheral Nervous System"),
        ("0012", "Tremor NOS", "Central & Peripheral Nervous System"),
        ("0014", "Fatigue", "Body as a Whole"),
        ("0015", "Weakness NOS", "Body as a Whole"),
        ("0016", "Oedema NOS", "Body as a Whole"),
        ("0017", "Rash NOS", "Skin & Appendages"),
        ("0018", "Pruritus NOS", "Skin & Appendages"),
        ("0020", "Palpitation", "Cardiovascular"),
        ("0027", "Myalgia NOS", "Musculo-Skeletal"),
        ("0004", "Diarrhoea NOS", "Gastrointestinal"),
        ("0005", "Abdominal pain NOS", "Gastrointestinal"),
        ("0035", "Anxiety NOS", "Psychiatric"),
        ("0013", "Insomnia NOS", "Psychiatric"),
    ]

    scored = []
    for code, term, soc in WHOART_SAMPLE:
        score = SequenceMatcher(None, symptom_text.lower(), term.lower()).ratio()
        scored.append((score, code, term, soc))

    scored.sort(reverse=True)
    return [
        {"rank": i + 1, "code": c, "term": t, "system_organ_class": s, "score": round(sc, 4)}
        for i, (sc, c, t, s) in enumerate(scored[:top_k])
    ]


def normalize_node(state: AgentState) -> AgentState:
    relations = state.get("relations", [])
    if not relations:
        return {**state, "normalized_pairs": [], "hitl_required": False}

    normalized_pairs = []

    for rel in relations:
        symptom_text = rel.get("symptom", "")
        candidates = _get_top_whoart_candidates(symptom_text)

        if not candidates:
            normalized_pairs.append({**rel, "normalized_term": None, "whoart_code": None})
            continue

        top = candidates[0]
        if top["score"] >= HITL_THRESHOLD:
            # Auto-select
            normalized_pairs.append({
                **rel,
                "normalized_term": top["term"],
                "whoart_code": top["code"],
                "whoart_score": top["score"],
            })
        else:
            # Needs HITL — store candidates and pause
            return {
                **state,
                "normalized_pairs": normalized_pairs,
                "hitl_required": True,
                "hitl_candidates": candidates,
                "hitl_pending_relation": rel,
            }

    return {**state, "normalized_pairs": normalized_pairs, "hitl_required": False}
