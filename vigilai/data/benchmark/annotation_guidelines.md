# Hinglish ADR Benchmark — Annotation Guidelines

## Format
JSONL — one JSON object per line in `train.jsonl` and `test.jsonl`.

## Schema
```json
{
  "id": "HIN_ADR_001",
  "hinglish_text": "Maine raat ko metformin 500mg li aur subah uthke ulti jaisi feeling thi",
  "english_translation": "I took metformin 500mg at night and in the morning I had nausea",
  "entities": [
    {"text": "metformin 500mg", "type": "DRUG", "start": 10, "end": 25},
    {"text": "ulti jaisi feeling", "type": "SYMPTOM", "start": 44, "end": 62}
  ],
  "relations": [
    {"drug": "metformin 500mg", "symptom": "ulti jaisi feeling", "type": "Causes-ADR"}
  ],
  "negative_example": false
}
```

## Entity Types
- **DRUG**: Any medication name, including brand and generic, with or without dosage
- **SYMPTOM**: Any adverse effect or symptom mentioned by patient
- **DOSAGE**: Dose amount when mentioned separately from drug name

## Relation Types
- **Causes-ADR**: Drug causes the adverse reaction
- **Treats-Indication**: Drug is being taken to treat the symptom (not an ADR)
- **No-Relation**: No causal relationship between the drug and symptom

## Target Distribution (300 examples)
| Category | Count |
|---|---|
| Single-drug ADR (positive) | 90 |
| Multi-drug ADR (positive) | 60 |
| Ambiguous — low confidence | 30 |
| Indication-only (negative) | 60 |
| No medical content (negative) | 30 |
| Negated symptom (negative) | 30 |
| **Total** | **300** |

## Key Hinglish Patterns

**Temporal markers (causal signals):**
lene ke baad, khane ke baad, pine ke baad, use karne ke baad, baad mein, phir se, shuru kiya, shuru ke baad

**Negation markers:**
nahi, nahin, nahi aaya, nahi hua, bilkul nahi, koi problem nahi

**Common ADR Hinglish terms:**
- chakkar aana / chakkar aa raha hai → dizziness
- ulti / ulti jaisi feeling → nausea/vomiting
- pet dard / pet mein dard → abdominal pain
- sar dard / sir mein dard → headache
- neend nahi aana → insomnia
- kamzori / thakaan → weakness/fatigue
- haath kaanpna → hand tremor
- dil ki dhadkan / dhadkan fast → palpitations
- rash / daane → skin rash
- khujli → pruritus/itching
- sujan → oedema/swelling
- dast / loose motion → diarrhoea
- qabz → constipation
- ghabrahat → anxiety

## Split
- `train.jsonl`: examples 001–240 (80%)
- `test.jsonl`: examples 241–300 (20%, held-out for F1 evaluation)
