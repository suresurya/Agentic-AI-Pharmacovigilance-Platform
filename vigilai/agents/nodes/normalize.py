import os
import json
import numpy as np
from agents.state import AgentState

HITL_THRESHOLD = 0.82
EMBEDDINGS_CACHE = os.path.join(os.path.dirname(__file__), "../../../data/whoart/whoart_embeddings.json")

_whoart_data: list[dict] | None = None


def _load_whoart_data() -> list[dict]:
    global _whoart_data
    if _whoart_data is not None:
        return _whoart_data
    if os.path.exists(EMBEDDINGS_CACHE):
        with open(EMBEDDINGS_CACHE) as f:
            _whoart_data = json.load(f)
        return _whoart_data
    # Fallback: load from DB without embeddings, use text similarity
    _whoart_data = _load_from_db_text_only()
    return _whoart_data


def _load_from_db_text_only() -> list[dict]:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        db_url = os.environ.get("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT code, term, system_organ_class FROM whoart_terms")
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"DB load failed: {e} — using built-in fallback")
        return _builtin_terms()


def _builtin_terms() -> list[dict]:
    return [
        {"code": "0001", "term": "Nausea NOS", "system_organ_class": "Gastrointestinal"},
        {"code": "0002", "term": "Vomiting NOS", "system_organ_class": "Gastrointestinal"},
        {"code": "0003", "term": "Nausea and vomiting", "system_organ_class": "Gastrointestinal"},
        {"code": "0004", "term": "Diarrhoea NOS", "system_organ_class": "Gastrointestinal"},
        {"code": "0005", "term": "Abdominal pain NOS", "system_organ_class": "Gastrointestinal"},
        {"code": "0006", "term": "Constipation", "system_organ_class": "Gastrointestinal"},
        {"code": "0010", "term": "Headache NOS", "system_organ_class": "Central & Peripheral Nervous System"},
        {"code": "0011", "term": "Dizziness NOS", "system_organ_class": "Central & Peripheral Nervous System"},
        {"code": "0012", "term": "Tremor NOS", "system_organ_class": "Central & Peripheral Nervous System"},
        {"code": "0013", "term": "Insomnia NOS", "system_organ_class": "Psychiatric"},
        {"code": "0014", "term": "Fatigue", "system_organ_class": "Body as a Whole"},
        {"code": "0015", "term": "Weakness NOS", "system_organ_class": "Body as a Whole"},
        {"code": "0016", "term": "Oedema NOS", "system_organ_class": "Body as a Whole"},
        {"code": "0017", "term": "Rash NOS", "system_organ_class": "Skin & Appendages"},
        {"code": "0018", "term": "Pruritus NOS", "system_organ_class": "Skin & Appendages"},
        {"code": "0020", "term": "Palpitation", "system_organ_class": "Cardiovascular"},
        {"code": "0022", "term": "Bradycardia NOS", "system_organ_class": "Cardiovascular"},
        {"code": "0027", "term": "Myalgia NOS", "system_organ_class": "Musculo-Skeletal"},
        {"code": "0029", "term": "Back pain", "system_organ_class": "Musculo-Skeletal"},
        {"code": "0035", "term": "Anxiety NOS", "system_organ_class": "Psychiatric"},
        {"code": "0037", "term": "Somnolence", "system_organ_class": "Central & Peripheral Nervous System"},
        {"code": "0063", "term": "Muscle cramps NOS", "system_organ_class": "Musculo-Skeletal"},
    ]


def _get_embedding(text: str) -> np.ndarray | None:
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
        return model.encode(text)
    except Exception:
        return None


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _text_similarity(a: str, b: str) -> float:
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _get_top_candidates(symptom_text: str, top_k: int = 3) -> list[dict]:
    terms = _load_whoart_data()
    symptom_emb = _get_embedding(symptom_text)

    scored = []
    for t in terms:
        term_text = t.get("term", "")
        emb = t.get("embedding")
        if symptom_emb is not None and emb is not None:
            score = _cosine_similarity(symptom_emb, np.array(emb))
        else:
            score = _text_similarity(symptom_text, term_text)
        scored.append((score, t))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "rank": i + 1,
            "code": t["code"],
            "term": t["term"],
            "system_organ_class": t.get("system_organ_class"),
            "score": round(sc, 4),
        }
        for i, (sc, t) in enumerate(scored[:top_k])
    ]


def normalize_node(state: AgentState) -> AgentState:
    relations = state.get("relations", [])
    if not relations:
        return {**state, "normalized_pairs": [], "hitl_required": False}

    normalized_pairs = []

    for rel in relations:
        symptom_text = rel.get("symptom", "")
        candidates = _get_top_candidates(symptom_text)

        if not candidates:
            normalized_pairs.append({**rel, "normalized_term": None, "whoart_code": None})
            continue

        top = candidates[0]
        if top["score"] >= HITL_THRESHOLD:
            normalized_pairs.append({
                **rel,
                "normalized_term": top["term"],
                "whoart_code": top["code"],
                "whoart_score": top["score"],
            })
        else:
            return {
                **state,
                "normalized_pairs": normalized_pairs,
                "hitl_required": True,
                "hitl_candidates": candidates,
                "hitl_pending_relation": rel,
            }

    return {**state, "normalized_pairs": normalized_pairs, "hitl_required": False}
