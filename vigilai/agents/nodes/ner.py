import os
import json
from agents.state import AgentState


# Known drug and symptom vocabularies for rule-based fallback
DRUG_VOCAB = {
    "paracetamol", "metformin", "amlodipine", "atorvastatin", "pantoprazole",
    "amoxicillin", "ibuprofen", "aspirin", "metoprolol", "omeprazole",
    "lisinopril", "losartan", "ciprofloxacin", "azithromycin", "doxycycline",
    "cetirizine", "loratadine", "ranitidine", "clopidogrel", "warfarin",
    "insulin", "glipizide", "glimepiride", "ramipril", "amlodipine",
    "sertraline", "fluoxetine", "diazepam", "alprazolam", "escitalopram",
    "metformin 500mg", "metformin 1000mg", "amlodipine 5mg", "aspirin 75mg",
}

SYMPTOM_VOCAB = {
    "chakkar": "dizziness", "ulti": "vomiting", "nausea": "nausea",
    "vomiting": "vomiting", "dizziness": "dizziness", "headache": "headache",
    "sar dard": "headache", "pet dard": "abdominal pain", "dard": "pain",
    "rash": "rash", "khujli": "pruritus", "sujan": "oedema",
    "kaanpna": "tremor", "tremor": "tremor", "weakness": "weakness",
    "kamzori": "weakness", "fatigue": "fatigue", "thakaan": "fatigue",
    "neend na aana": "insomnia", "insomnia": "insomnia",
    "dil ki dhadkan": "palpitations", "palpitations": "palpitations",
    "breathlessness": "dyspnoea", "sans": "dyspnoea",
    "chest pain": "chest pain", "chhati mein dard": "chest pain",
    "loose motion": "diarrhoea", "dast": "diarrhoea",
    "constipation": "constipation", "qabz": "constipation",
    "anxiety": "anxiety", "ghabrahat": "anxiety",
    "depression": "depression", "udaasi": "depression",
    "ulti jaisi feeling": "nausea", "chakkar aana": "dizziness",
    "haath kaanpna": "hand tremor", "sar mein dard": "headache",
    "pet mein dard": "abdominal pain", "neend nahi": "insomnia",
    "bahut thaka": "fatigue", "aankhein dhundhli": "visual disturbance",
    "zyada pyaas": "polydipsia", "zyada peshab": "polyuria",
}


def _find_entity_spans(text: str, vocab: set, entity_type: str) -> list[dict]:
    import re
    text_lower = text.lower()
    found = []
    # Try multi-word first, then single
    sorted_terms = sorted(vocab, key=len, reverse=True)
    covered = set()
    for term in sorted_terms:
        term_lower = term.lower()
        for match in re.finditer(re.escape(term_lower), text_lower):
            start, end = match.start(), match.end()
            if any(start < c < end or c == start for c in covered):
                continue
            found.append({
                "text": text[start:end],
                "type": entity_type,
                "start": start,
                "end": end,
                "confidence": 0.85,
                "source_model": "rule-based",
            })
            for i in range(start, end):
                covered.add(i)
    return found


def _claude_ner_fallback(text: str) -> list[dict]:
    """Use Claude Sonnet to extract entities when confidence is low."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
        prompt = f"""Extract medical entities from this Hinglish patient narrative.

Narrative: "{text}"

Return ONLY a JSON array of entities. Each entity must have:
- text: the exact text span from the narrative
- type: one of "drug", "symptom", or "dosage"
- start: character start index
- end: character end index
- confidence: float between 0 and 1

Example: [{{"text": "metformin", "type": "drug", "start": 6, "end": 15, "confidence": 0.95}}]

Return ONLY the JSON array, no other text."""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        entities = json.loads(raw.strip())
        for e in entities:
            e["source_model"] = "claude-sonnet"
        return entities
    except Exception as e:
        print(f"Claude NER fallback failed: {e}")
        return []


def ner_node(state: AgentState) -> AgentState:
    text = state.get("clean_text") or state["raw_text"]

    # Rule-based extraction
    drug_entities = _find_entity_spans(text, DRUG_VOCAB, "drug")
    symptom_entities = _find_entity_spans(text, set(SYMPTOM_VOCAB.keys()), "symptom")

    entities = drug_entities + symptom_entities

    # If nothing found, fall back to Claude
    if not entities:
        entities = _claude_ner_fallback(text)

    # Normalise symptom text using vocab mapping
    for e in entities:
        if e["type"] == "symptom":
            mapped = SYMPTOM_VOCAB.get(e["text"].lower())
            if mapped:
                e["normalized_text"] = mapped

    # Sort by position
    entities.sort(key=lambda x: x.get("start", 0))

    return {**state, "entities": entities}
