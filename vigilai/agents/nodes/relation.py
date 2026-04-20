import os
import json
from itertools import product
from agents.state import AgentState
from agents.prompts.relation_prompt import RELATION_PROMPT


def _call_claude(clean_text: str, drug_span: str, symptom_span: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    prompt = RELATION_PROMPT.format(
        clean_text=clean_text,
        drug_span=drug_span,
        symptom_span=symptom_span,
    )
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def relation_node(state: AgentState) -> AgentState:
    text = state.get("clean_text") or state["raw_text"]
    entities = state.get("entities", [])

    drugs = [e for e in entities if e["type"] == "drug"]
    symptoms = [e for e in entities if e["type"] == "symptom"]

    if not drugs or not symptoms:
        return {**state, "relations": []}

    relations = []
    for drug, symptom in product(drugs, symptoms):
        try:
            result = _call_claude(text, drug["text"], symptom["text"])
            relation_type = result.get("relation_type", "No-Relation")
            if relation_type in ("Causes-ADR", "Possible-ADR"):
                relations.append({
                    "drug": drug["text"],
                    "drug_start": drug.get("start"),
                    "drug_end": drug.get("end"),
                    "symptom": symptom["text"],
                    "symptom_start": symptom.get("start"),
                    "symptom_end": symptom.get("end"),
                    "relation_type": relation_type,
                    "confidence": result.get("confidence", 0.5),
                    "evidence": {
                        "drug_span": drug["text"],
                        "reaction_span": symptom["text"],
                        "temporal_marker": result.get("temporal_marker"),
                        "temporal_marker_translation": result.get("temporal_marker_translation"),
                        "causal_pattern": result.get("causal_pattern"),
                        "negation_detected": result.get("negation_detected", False),
                        "plain_language_reason": result.get("plain_language_reason"),
                    },
                })
            elif relation_type == "Causes-ADR":
                # already handled above
                pass
        except Exception as e:
            print(f"Relation extraction failed for {drug['text']} × {symptom['text']}: {e}")

    # Sort by confidence descending
    relations.sort(key=lambda r: r["confidence"], reverse=True)

    return {**state, "relations": relations}
