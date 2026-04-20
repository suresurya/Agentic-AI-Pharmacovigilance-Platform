import os
import uuid
import psycopg2
from agents.state import AgentState


def _get_conn():
    db_url = os.environ.get("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")
    return psycopg2.connect(db_url)


def report_node(state: AgentState) -> AgentState:
    narrative_id = state["narrative_id"]
    normalized_pairs = state.get("normalized_pairs", [])

    if not normalized_pairs:
        return {**state, "report_id": None}

    report_ids = []
    try:
        conn = _get_conn()
        cur = conn.cursor()

        for pair in normalized_pairs:
            report_id = str(uuid.uuid4())
            evidence = pair.get("evidence", {})

            cur.execute(
                """
                INSERT INTO adr_reports
                    (id, narrative_id, relation_type, confidence, evidence,
                     normalized_term, whoart_code, officer_status)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, 'pending')
                """,
                (
                    report_id,
                    narrative_id,
                    pair.get("relation_type", "Causes-ADR"),
                    pair.get("confidence", 0.5),
                    __import__("json").dumps(evidence),
                    pair.get("normalized_term"),
                    pair.get("whoart_code"),
                ),
            )
            report_ids.append(report_id)

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Report node DB write failed: {e}")

    return {**state, "report_id": report_ids[0] if report_ids else None}
