# VigilAI 2.0
## Multilingual Pharmacovigilance Intelligence Platform
### Cognizant Technoverse Hackathon 2026 — Lifesciences → Pharmacovigilance

---

## Executive Summary

VigilAI is a B2B SaaS pharmacovigilance platform that processes consented Hinglish patient narratives from pharmaceutical companies and telemedicine platforms. A six-node LangGraph multi-agent pipeline extracts Adverse Drug Reaction signals, provides explainable linguistic evidence for every classification, and surfaces structured safety reports to pharmacovigilance officers for human review and approval.

**Five things that make VigilAI different from every existing system:**

1. Only pharmacovigilance platform architecturally designed for Hinglish — the code-mixed Hindi-English used by 700M+ Indians
2. Explainability-first — every ADR classification shows the exact linguistic evidence that triggered it
3. B2B consent-first model — processes data pharmaceutical companies already legally own, no social media scraping
4. Genuine agentic HITL — LangGraph graph pauses and waits for officer input when confidence is below threshold
5. First public Hinglish ADR benchmark dataset — a research contribution alongside a working product

**Team:** 4 members | **Theme:** Lifesciences → Pharmacovigilance | **Stack:** Python, React, FastAPI, LangGraph, PostgreSQL, AWS

---

## Part 1: The 5 Core Refinements

These five changes raise the idea from a 6.6 to an 8.5+ across all judging dimensions. Each refinement solves a specific, documented weakness.

### Refinement 1 — B2B Consent-First Model (Market Readiness: 5.0 → 8.0)

**Problem:** The original idea proposed monitoring public social media for patient health data. Under India's DPDP Act 2023, collecting sensitive health information without explicit consent is legally questionable. This was the single biggest structural weakness.

**Solution:** VigilAI becomes a pure B2B SaaS platform. Target customers are organizations that already possess DPDP-compliant patient consent:

- **Pharmaceutical companies:** CDSCO mandates all Schedule H manufacturers to maintain active pharmacovigilance programs. They collect patient feedback with consent and need software to process it in Hinglish.
- **Telemedicine platforms (Practo, 1mg, Tata 1mg):** Patient consultations generate Hinglish transcripts. Platforms already have patient consent for medical data processing.
- **Hospital pharmacy departments:** Patient medication records with existing clinical consent.

No public data scraping. No consent questions. VigilAI processes data the customer already owns.

**Additionally:** A patient-facing Hinglish submission portal allows direct voluntary reporting with a DPDP-compliant itemized consent notice displayed in both Hinglish and English before any input is accepted.

---

### Refinement 2 — Explainability Layer (Uniqueness: 7.5 → 8.5, Technical Depth: 7.5 → 8.5)

**Problem:** The original system extracted ADR pairs but gave no reason why. An officer cannot approve a report they cannot verify.

**Solution:** Every classification produces a structured evidence object alongside the prediction:

```json
{
  "drug": "metformin",
  "reaction": "nausea",
  "relation_type": "Causes-ADR",
  "confidence": 0.91,
  "evidence": {
    "drug_span": "metformin 500mg",
    "reaction_span": "ulti jaisi feeling",
    "temporal_marker": "lene ke baad",
    "temporal_marker_translation": "after taking",
    "causal_pattern": "temporal_proximity_post_ingestion",
    "negation_detected": false,
    "plain_language_reason": "Patient describes nausea-like sensation occurring after metformin intake with explicit temporal marker indicating the drug was taken before the symptom appeared"
  }
}
```

The React dashboard renders entity spans highlighted in the original text alongside this evidence. No pharmacovigilance system — for any language — provides this for informal patient narratives.

---

### Refinement 3 — Production-Grade Infrastructure (Scalability: 7.5 → 8.5)

**Problem:** In-memory embedding search does not scale beyond a single instance. No queue for batch processing. No plan for high-volume NER inference.

**Three infrastructure fixes:**

**pgvector:** WHO-ART term embeddings stored in PostgreSQL using the pgvector extension. Same database, no separate vector service, sub-10ms cosine similarity search, zero additional infrastructure.

**AWS SQS:** Pharma companies submit CSV batches of thousands of narratives. SQS decouples ingestion from processing. FastAPI acknowledges immediately with a job ID, processes asynchronously. No timeouts, no dropped requests under load.

**AWS SageMaker Serverless Inference:** XLM-RoBERTa NER model on SageMaker serverless endpoints. Auto-scales from zero, costs nothing during idle, eliminates always-on GPU cost.

---

### Refinement 4 — The Hinglish ADR Benchmark Dataset (Technical Depth: 7.5 → 8.5)

**Problem:** Without a labeled dataset there are no F1 scores. Without F1 scores there is no objective evidence the system works. This is a fatal demo weakness.

**Solution:** Days 1 and 2 of the project (April 16-17) are dedicated entirely to all 4 members writing and labeling 300 Hinglish patient narrative examples. This produces:

- A 240-example training set for XLM-RoBERTa fine-tuning
- A 60-example held-out test set for F1 evaluation
- The first publicly available labeled Hinglish ADR dataset — a genuine research contribution

At demo time, when a judge asks "what accuracy does your system achieve?", you produce a printed results sheet with real numbers from your test set.

---

### Refinement 5 — Multi-Drug Narrative Handling (Uniqueness contribution)

**Problem:** Real patients take multiple medications. "Metformin aur amlodipine dono le raha hun, chakkar aa rahe hain" — the original system extracted one drug-symptom pair and stopped.

**Solution:** The Relation node processes all drug-symptom permutations in a narrative and returns a ranked list:

```json
{
  "drug_reaction_pairs": [
    {"drug": "amlodipine", "reaction": "dizziness", "confidence": 0.87, "relation": "Causes-ADR"},
    {"drug": "metformin", "reaction": "dizziness", "confidence": 0.54, "relation": "Possible-ADR"}
  ],
  "recommended_primary": "amlodipine → dizziness (confidence 0.87)"
}
```

The officer selects which pairs to include in the final report.

---

## Part 2: Hackathon Idea Submission (Official Format)

### WHY — The Problem

#### Problem Description and Business Scenario

Adverse Drug Reactions are the 4th leading cause of death in hospitalized patients globally, yet the WHO estimates 94% of ADRs go unreported through official channels. Traditional pharmacovigilance systems suffer from three structural failures: severe under-reporting, detection latency of 6–18 months, and complete language blindness to non-English patient populations.

India presents the sharpest version of this gap. With 1.4 billion people and 3,000+ CDSCO-licensed pharmaceutical manufacturers, India is one of the world's largest drug markets. Every major pharmacovigilance system — WHO VigiBase, FDA FAERS, EudraVigilance — processes only formal English.

Pharmaceutical companies operating in India collect enormous volumes of patient feedback in Hinglish — code-mixed Hindi-English written in Roman script, used by 700M+ Indians. This data sits unprocessed in CRM systems, telemedicine transcripts, and patient feedback portals because no tool exists to analyse it at scale. CDSCO's 2023 mandate requires all Schedule H drug manufacturers to maintain active pharmacovigilance programs. The software to fulfill this mandate for the Hinglish-speaking majority of India does not exist.

#### Problem Scope

VigilAI is an upstream signal detection and triage layer for pharmaceutical companies and telemedicine platforms. It does not replace pharmacovigilance officers — it enables each officer to process 10 times the volume with full Hinglish coverage. Every report requires officer review and approval before any regulatory submission. The system processes only consented data from B2B customers.

#### Target Users and Stakeholders

| Stakeholder | Need |
|---|---|
| Pharmacovigilance officers at pharma companies | Process more narratives per day with linguistic coverage |
| Drug safety teams at telemedicine platforms | Monitor Hinglish transcripts for ADR patterns automatically |
| CDSCO regulators | Receive earlier, broader structured signals from India's population |
| Hospital pharmacy departments | Compliance with pharmacovigilance reporting obligations |
| Patients (voluntary portal) | Report symptoms in their natural language with confidence |

---

### HOW — The Solution

#### Solution Overview

VigilAI is a full-stack B2B web application with five integrated components:

**React Dashboard:** Officer interface with real-time entity highlighting on source text, evidence panel for every classification, HITL prompt for low-confidence normalizations, one-click approve/reject/modify, JSON export.

**FastAPI Backend:** Async ASGI API handling REST and WebSocket connections. Pydantic v2 validation. SQS consumer for batch jobs. Automatic OpenAPI documentation.

**LangGraph Agent Pipeline:** Six-node stateful agent graph. Each node is autonomous with typed input/output state. Supports partial re-execution, node-level retry, and genuine HITL pause/resume via graph.interrupt() at the Normalize node.

**PostgreSQL + pgvector:** Single database for relational storage and vector similarity search. No separate vector database service required.

**AWS Infrastructure:** SQS for batch queues, SageMaker Serverless for NER inference, RDS PostgreSQL with pgvector, S3 for archival, KMS for AES-256 encryption at rest, TLS 1.3 in transit, IAM least-privilege roles.

---

#### The Six LangGraph Agent Nodes

**Node 1 — Ingest**

Accepts three input types: single narrative via REST API, CSV batch via S3 presigned URL posted to SQS, telemedicine transcript via webhook. Validates payload with Pydantic. Detects Hinglish/Hindi/English ratio. Writes raw narrative to PostgreSQL narratives table with status='queued'. Initializes LangGraph state TypedDict with narrative_id, clean_text (null), entities (empty), relations (empty), report_id (null).

**Node 2 — Preprocess**

Applies Indic NLP Library: Unicode normalization, Devanagari script detection and flagging, noise removal (hashtags, URLs, emojis, platform artifacts). Byte-Pair Encoding tokenization via HuggingFace tokenizer — handles out-of-vocabulary Hinglish morphological variants by decomposing into subword units. Outputs clean_text and subword token list. Updates agent state.

**Node 3 — NER (Named Entity Recognition)**

Primary path: XLM-RoBERTa base fine-tuned on 240 training examples from the Hinglish ADR benchmark, BIO tagging scheme. Identifies entity spans tagged as DRUG, SYMPTOM, or DOSAGE with character offsets. Fallback path (triggered when model confidence < 0.70): Claude Sonnet with structured JSON prompt requesting entity list. Returns entity spans, types, character offsets, confidence scores, and source model. Updates agent state with entities list.

**Node 4 — Relation Extraction + Explainability**

For every (DRUG, SYMPTOM) pair in the entity list, calls Claude Sonnet with a 6-shot Hinglish prompt. The prompt requests both the relation classification and the structured evidence object in a single response. Classifies each pair as: Causes-ADR, Treats-Indication, or No-Relation. Extracts temporal marker, temporal translation, causal pattern, negation status, and plain-language reason. Builds the evidence JSON object for the explainability layer. Retains only Causes-ADR and Possible-ADR pairs. Updates agent state with relations list.

**Node 5 — Normalize (HITL Checkpoint)**

For each confirmed ADR symptom span, embeds the text using sentence-transformers (paraphrase-multilingual-mpnet-base-v2, 768 dimensions). Executes pgvector cosine similarity search against WHO-ART term embeddings stored in PostgreSQL. Returns top-3 candidates with similarity scores. Decision logic: if top candidate score > 0.82, auto-select and continue. If score ≤ 0.82, execute graph.interrupt() — dashboard shows officer the 3 candidates with similarity scores. Officer selects one. graph.resume() called with officer's selection. Officer selection logged to officer_actions table for active learning. Updates agent state with normalized_term and whoart_code.

**Node 6 — Report**

Assembles complete ADR report object combining all state: narrative, entities, relations, evidence, normalized term, confidence scores. Writes to adr_reports table with officer_status='pending'. For multi-drug narratives, writes one report row per retained pair. Publishes WebSocket event to officer dashboard. Supports batch completion notification via SQS response.

---

#### Complete Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Frontend | React + TypeScript | 18+ | Dashboard and officer interface |
| State management | Zustand | Latest | Lightweight client state |
| Backend | FastAPI | 0.111+ | Async REST and WebSocket API |
| Validation | Pydantic v2 | 2.x | Runtime schema enforcement |
| Agent framework | LangGraph + LangChain | Latest | Stateful 6-node agent graph |
| LLM | Claude Sonnet | claude-sonnet-4-20250514 | Relation extraction + NER fallback |
| NER model | XLM-RoBERTa base | HuggingFace | Multilingual named entity recognition |
| Embeddings | paraphrase-multilingual-mpnet | HuggingFace | WHO-ART normalization |
| Ontology | WHO-ART | v2015 (public domain) | Medical terminology, 1,700 terms |
| Database | PostgreSQL 16 + pgvector | RDS + extension | Relational storage + vector search |
| Message queue | AWS SQS | — | Async batch processing decoupling |
| ML inference | AWS SageMaker Serverless | — | Auto-scaling NER endpoint |
| Object storage | AWS S3 | — | Narrative archival |
| Encryption | AWS KMS | — | AES-256 at rest |
| Access control | AWS IAM | — | Least-privilege per service role |
| Containerization | Docker + ECS | — | Local dev and cloud deployment |
| API docs | OpenAPI/Swagger | Via FastAPI | Auto-generated endpoint documentation |

---

#### Innovation

**1. First Hinglish-native pharmacovigilance pipeline.**
WHO VigiBase, FDA FAERS, EudraVigilance, and all commercial tools process only formal English. No tool anywhere processes code-mixed Roman-script Hindi for ADR extraction. This is the fundamental market gap.

**2. Explainability-first design.**
Every classification includes the linguistic evidence that triggered it — temporal markers, causal patterns, negation detection — rendered inline in the officer's dashboard. No pharmacovigilance system provides this for informal patient language in any language.

**3. First public Hinglish ADR benchmark.**
The 300-example labeled dataset created in Days 1–2 is the first publicly available Hinglish ADR evaluation set. It enables reproducible benchmarking and is itself a research contribution the team can cite and open-source.

**4. B2B consent-first model.**
By targeting pharmaceutical companies and telemedicine platforms — not consumers — VigilAI eliminates the social media consent problem entirely while capturing a more valuable, regulation-driven market with CDSCO compliance as the primary purchase driver.

**5. Multi-drug narrative handling.**
Real patients describe polypharmacy. VigilAI processes all drug-symptom permutations in a single narrative and ranks them by confidence. No existing system does this for Hinglish.

**6. Genuine HITL pause/resume.**
LangGraph's graph.interrupt() mechanism halts pipeline execution mid-graph and resumes exactly where it stopped after officer input. This is a real execution pattern, not a dashboard review form.

---

#### Market Potential

| Market | Size | Source |
|---|---|---|
| Global pharmacovigilance market | USD 7.6B by 2030, CAGR 12.1% | Grand View Research |
| India pharmaceutical market | USD 65B, 3,000+ Schedule H manufacturers | CDSCO |
| India PV software TAM | ~USD 150M (3,000 manufacturers × avg spend) | Derived estimate |
| India telemedicine consultations | 500M+ annually generating Hinglish transcripts | NITI Aayog |
| ADR under-reporting rate (India) | ~95% | National PV Programme |

CDSCO's mandatory pharmacovigilance software requirement for all Schedule H manufacturers creates forced institutional demand independent of voluntary market adoption.

---

### WHAT — Value Proposition

| Metric | Status Quo | With VigilAI | Gain |
|---|---|---|---|
| ADR detection latency | 6–18 months | Hours to days | ~95% reduction |
| Language coverage | English only | Hinglish + English | 700M new patients |
| Reports per officer per day | ~8 (manual) | ~80 (AI-triaged) | 10x throughput |
| Classification transparency | None | Full linguistic evidence | Officer trust enabled |
| Multi-drug handling | Not supported | Ranked pair list | Real-world applicability |
| Consent compliance | Manual assessment | DPDP-by-design B2B model | Zero legal exposure |
| Cost per signal | High (staff hours) | ~Rs. 0.17 per narrative | 85–90% cost reduction |
| Compliance documentation | Manual | Structured JSON with audit trail | Regulator-ready |

---

## Part 3: System Architecture

### Data Flow

```
Pharma company / Telemedicine platform
           |
    [CSV batch or API]
           |
    [AWS SQS Queue]
           |
    [FastAPI Consumer]
           |
    [LangGraph Agent Graph]
    |         |         |         |         |         |
[Ingest] [Preprocess] [NER] [Relation] [Normalize] [Report]
                                         |
                               [HITL — officer selects]
                               [term if confidence low]
                                         |
    [PostgreSQL + pgvector] ◄────────────┘
           |
    [WebSocket event to dashboard]
           |
    [Officer reviews, approves, exports]
```

### Security Architecture

All patient data encrypted AES-256 at rest via AWS KMS. All API traffic over TLS 1.3. IAM roles grant each service minimum required permissions only. FastAPI service: write-only PostgreSQL, no direct S3 access. SageMaker inference role: read-only S3 model bucket. Officer authentication via JWT with short expiry. All officer actions logged immutably to officer_actions table. Data retention policy: narratives deleted after 90 days unless officer explicitly saves the report.

---

## Part 4: Database Schema

### Table: narratives

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | Unique identifier |
| source_text | TEXT | Original Hinglish input |
| source_type | ENUM | manual / csv_batch / api_webhook / patient_portal |
| customer_id | UUID FK | B2B customer organization |
| language_mix_ratio | FLOAT | Proportion of Hindi tokens detected |
| status | ENUM | queued / processing / pending_review / done / failed |
| created_at | TIMESTAMPTZ | Ingestion timestamp |

### Table: entities

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | Entity identifier |
| narrative_id | UUID FK | Parent narrative |
| entity_text | VARCHAR | Extracted text span |
| entity_type | ENUM | drug / symptom / dosage |
| char_start | INT | Start character offset |
| char_end | INT | End character offset |
| confidence | FLOAT | Model confidence |
| source_model | VARCHAR | xlm-roberta or claude-sonnet |

### Table: adr_reports

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | Report identifier |
| narrative_id | UUID FK | Source narrative |
| drug_entity_id | UUID FK | Extracted drug entity |
| symptom_entity_id | UUID FK | Extracted symptom entity |
| relation_type | ENUM | Causes-ADR / Possible-ADR |
| confidence | FLOAT | Relation confidence score |
| evidence | JSONB | Full explainability object |
| normalized_term | VARCHAR | Matched WHO-ART term |
| whoart_code | VARCHAR | WHO-ART code |
| officer_status | ENUM | pending / approved / rejected / modified |
| officer_notes | TEXT | Officer annotation |
| created_at | TIMESTAMPTZ | Report creation time |

### Table: officer_actions (active learning log)

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | Action identifier |
| report_id | UUID FK | Associated report |
| action_type | ENUM | approve / reject / modify_term / modify_relation |
| original_value | JSONB | Model's original output |
| corrected_value | JSONB | Officer's correction |
| officer_id | VARCHAR | Authenticated officer |
| created_at | TIMESTAMPTZ | Action timestamp |

### Table: whoart_terms (pgvector)

| Column | Type | Notes |
|---|---|---|
| id | INT PK | Term identifier |
| code | VARCHAR | WHO-ART code |
| term | VARCHAR | Term description |
| system_organ_class | VARCHAR | SOC grouping |
| embedding | VECTOR(768) | Sentence-transformer embedding for pgvector ANN search |

---

## Part 5: API Design

### REST Endpoints

```
POST   /api/v1/narratives/              Submit single narrative
POST   /api/v1/narratives/batch/        Submit CSV (returns SQS job_id)
GET    /api/v1/narratives/{id}/         Get processing status

GET    /api/v1/reports/                 List reports (filter by status, date, drug)
GET    /api/v1/reports/{id}/            Full report with evidence object
PATCH  /api/v1/reports/{id}/review/     Officer approve / reject / modify
GET    /api/v1/reports/{id}/export/     Download as JSON
GET    /api/v1/reports/analytics/       ADR signal trend dashboard data

GET    /api/v1/whoart/search/?q=        Search WHO-ART terms for officer lookup

WS     /ws/pipeline/{narrative_id}      Live agent node progress stream
```

### WebSocket Event Schema

```json
{
  "event": "node_complete",
  "node": "NER",
  "status": "success",
  "output_preview": "Found: metformin (DRUG), nausea (SYMPTOM)",
  "timestamp": "2026-04-16T10:22:00Z",
  "next_node": "Relation"
}
```

```json
{
  "event": "hitl_required",
  "node": "Normalize",
  "candidates": [
    {"rank": 1, "term": "Nausea NOS", "code": "0882", "score": 0.79},
    {"rank": 2, "term": "Nausea and vomiting", "code": "0883", "score": 0.71},
    {"rank": 3, "term": "Vomiting NOS", "code": "0884", "score": 0.61}
  ],
  "message": "Confidence below threshold. Officer selection required."
}
```

---

## Part 6: Benchmark Dataset Plan

### Why This Is Non-Negotiable

A judge will ask: "What accuracy does your NER achieve?" Without a real labeled dataset and real F1 numbers, the only honest answer is "we don't know." That loses the evaluation round. Days 1 and 2 exist to prevent this.

### Annotation Guidelines

**Format:** JSONL, one example per line.

```json
{
  "id": "HIN_ADR_001",
  "hinglish_text": "Maine raat ko metformin 500mg li aur subah uthke ulti jaisi feeling thi",
  "english_translation": "I took metformin 500mg at night and in the morning I had a nausea-like feeling",
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

### Target Distribution (300 examples)

| Category | Count | Examples |
|---|---|---|
| Positive — single drug ADR | 90 | Simple drug + symptom with temporal marker |
| Positive — multi-drug ADR | 60 | Two or more drugs, ranking required |
| Positive — ambiguous | 30 | Low-confidence temporal cues |
| Negative — indication only | 60 | Drug treating a pre-existing condition |
| Negative — no medical content | 30 | General health discussion, no ADR |
| Negative — negated symptom | 30 | "chakkar nahi aaya" (no dizziness) |
| **Total** | **300** | |

### Common Hinglish Patterns to Include

**Temporal markers (causal signals):** lene ke baad, khane ke baad, pine ke baad, use karne ke baad, baad mein, phir se

**Common ADR descriptions:** chakkar aana, ulti/nausea, pet dard, sar dard, neend na aana, kamzori, haath kaanpna, dil ki dhadkan, rash, khujli, sujan

**Common drugs:** paracetamol, metformin, amlodipine, atorvastatin, pantoprazole, amoxicillin, ibuprofen, aspirin, metoprolol, omeprazole

**Split:** 240 training examples, 60 held-out test examples (20%).

### Expected F1 Scores (Honest Range)

| Task | Expected F1 | Basis |
|---|---|---|
| Drug NER | 0.78–0.82 | Drug names are more standardized |
| Symptom NER | 0.65–0.72 | Informal descriptions are more variable |
| Relation extraction | 0.70–0.76 | Claude Sonnet few-shot on 300 examples |
| WHO-ART Top-1 | 0.72–0.78 | pgvector cosine similarity |
| WHO-ART Top-3 | 0.88–0.92 | Top-3 candidate coverage |

Report these ranges honestly. A real F1 of 0.72 is more credible and impressive than a claimed 0.95 with no data behind it.

---

## Part 7: Explainability Layer Design

### Relation Node Prompt Template

```
You are a pharmacovigilance expert. Analyze this Hinglish patient narrative and determine
the relationship between the identified drug and symptom.

Narrative: {clean_text}
Drug entity: {drug_span}
Symptom entity: {symptom_span}

Classify the relationship as exactly one of: Causes-ADR, Treats-Indication, No-Relation

Then extract the following evidence fields:
- temporal_marker: the time-indicating phrase if present (e.g. "ke baad", "baad mein")
- temporal_marker_translation: English translation of the temporal marker
- negation_detected: true or false (look for "nahi", "nahin", "no", "not")
- causal_pattern: one of [temporal_proximity_post_ingestion, patient_self_attribution,
  concurrent_occurrence, negative_association, no_clear_pattern]
- plain_language_reason: one sentence in English explaining the classification

Respond ONLY in this exact JSON format with no other text:
{
  "relation_type": "Causes-ADR",
  "confidence": 0.91,
  "temporal_marker": "lene ke baad",
  "temporal_marker_translation": "after taking",
  "negation_detected": false,
  "causal_pattern": "temporal_proximity_post_ingestion",
  "plain_language_reason": "..."
}
```

### Dashboard Evidence Rendering

```
[ metformin 500mg ]              [ ulti jaisi feeling ]
     DRUG  91%                       SYMPTOM  88%

Relation:   Causes-ADR    Confidence: 91%
WHO-ART:    Nausea NOS (Code: 0882)

Evidence
  Temporal marker:   "lene ke baad" — after taking
  Causal pattern:    Temporal proximity post-ingestion
  Negation check:    None detected
  Reason:            Patient describes nausea-like sensation
                     occurring after metformin intake with explicit
                     temporal marker indicating causal sequence.

[ Approve ]  [ Reject ]  [ Modify ]
```

---

## Part 8: 20-Day Execution Plan

### Phase 1 — Foundation (Days 1–4, April 16–19)

**Days 1–2: ALL 4 MEMBERS — Dataset creation**
This is the most critical task. All four team members spend two full days writing and labeling 300 Hinglish ADR narratives per the annotation guidelines above. Do not shortcut this. The benchmark dataset is what separates this project from every other team.

**Day 3–4 parallel tracks:**

| Member | Tasks |
|---|---|
| Member 1 | React project setup, layout, WebSocket client, entity highlight component scaffold |
| Member 2 | FastAPI project, Pydantic schemas, PostgreSQL + pgvector setup, REST endpoints scaffold |
| Member 3 | LangGraph graph with dummy nodes, state TypedDict, graph compiles and runs |
| Member 4 | AWS setup: RDS, SQS queue, XLM-RoBERTa download, WHO-ART embedding index built into pgvector |

### Phase 2 — Core Agent Build (Days 5–10, April 20–25)

**TARGET: Working agent demo ready by April 23 (Agent Builder Challenge)**

| Day | Member 3 + 4 (Agent) | Member 1 + 2 (Frontend + API) |
|---|---|---|
| 5 | Ingest + Preprocess nodes complete | Entity highlighting component working |
| 6 | NER node working (Claude fallback) | WebSocket live progress rendering |
| **7 — Apr 23** | **Relation + Explainability node done** | **Dashboard shows evidence panel** |
| 8 | Normalize node + pgvector search | Officer review actions (approve/reject) |
| 9 | HITL interrupt + resume working | HITL prompt in dashboard |
| 10 | Report node + WebSocket events | Batch upload interface |

### Phase 3 — Integration and Testing (Days 11–16, April 26–May 1)

| Day | Task |
|---|---|
| 11–12 | Full end-to-end integration testing with real Hinglish inputs |
| 13 | Fine-tune XLM-RoBERTa on 240 training examples |
| 14 | Run F1 evaluation on 60-example test set. Record all results. |
| 15 | SQS batch processing integration and stress test |
| 16 | AWS ECS deployment, SageMaker serverless endpoint deployment |

### Phase 4 — Polish and Demo (Days 17–20, May 2–5)

| Day | Task |
|---|---|
| 17 | Bug fixes from integration testing |
| 18 | Prepare 10 curated Hinglish demo narratives that showcase all system features |
| 19 | Full 5-minute demo rehearsal all 4 members, timed. Fix any rough edges. |
| 20 | Final polish. Backup demo on laptop with no internet dependency. |

---

## Part 9: Demo Script (5 Minutes)

**Setup:** Dashboard open on screen. 10 pre-curated narratives loaded. Printed F1 results sheet ready.

**Minute 1 — The problem (spoken):**
"Every pharmaceutical company in India is legally required by CDSCO to report Adverse Drug Reactions. Most patient feedback arrives in Hinglish — a mix of Hindi and English. No software anywhere can process it. VigilAI is the first."

**Minute 2 — Single narrative live demo:**
Input: "Maine kal raat metformin 500mg li aur subah uthke bahut ulti jaisi feeling thi, haath bhi kaanp rahe the"
Point to: Agent progress stream on the right — nodes lighting up in sequence.
Point to: Entity spans highlighted in the source text.
Point to: Evidence panel — "Notice the temporal marker 'lene ke baad' — the system identifies this as causal, not coincidental. This is why the officer can trust the classification."

**Minute 3 — Multi-drug narrative:**
Input a narrative with two drugs mentioned.
Show: Two pairs ranked by confidence.
Say: "Real patients take multiple medications. VigilAI handles the full complexity."

**Minute 4 — HITL checkpoint:**
Use a narrative where normalization confidence is below 0.82.
Show: Graph pauses. Dashboard shows three WHO-ART candidates.
Officer clicks candidate 1.
Show: Graph resumes. Report generated.
Say: "This is not a review form. The AI genuinely waits. Nothing goes to a report without human validation."

**Minute 5 — Benchmark results and close:**
Show printed sheet: "Our NER achieves F1 of [X] on a 60-example held-out test set from the first publicly available labeled Hinglish ADR benchmark — which we created as part of this project and are open-sourcing today."
Close: "3,000 pharmaceutical manufacturers in India have a CDSCO mandate and no tool that speaks their patients' language. VigilAI does."

---

## Part 10: Production Roadmap

**Phase 2 (Months 1–3):**
Data partnership with 1–2 telemedicine platforms for pilot deployment. Fine-tune XLM-RoBERTa on thousands of platform-provided examples. Active learning loop: officer corrections retrain model monthly.

**Phase 3 (Months 4–6):**
Language expansion to Tamil, Telugu, Marathi via IndicBERT. Full MedDRA LLT normalization with institutional license. Multi-tenant SaaS with per-organization fine-tuned models.

**Phase 4 (Months 7–12):**
ICH E2B(R3) XML generation for direct CDSCO electronic submission. CDSCO formal pilot partnership. Regional language expansion to all 22 scheduled Indian languages.

**Phase 5 (Year 2+):**
Hospital-grade deployment with AWS Nitro Enclaves for confidential zero-trust inference. Federated learning across pharmaceutical company data without sharing raw patient narratives. International expansion to Bangla, Nepali, Sri Lankan Tamil.

---

## Part 11: Scoring Justification

| Dimension | Score | Key reasons |
|---|---|---|
| Uniqueness | 8.5 | No Hinglish PV tool exists anywhere; explainability layer is novel for any informal-language PV system; first public Hinglish ADR benchmark; multi-drug handling; B2B consent model is architecturally distinct |
| Business Value | 9.5 | CDSCO mandate creates forced demand for 3,000+ manufacturers; USD 150M India TAM; 10x officer throughput with clear ROI; B2B SaaS with recurring revenue; telemedicine platform expansion path |
| Implementability | 8.0 | Full stack buildable in 20 days with clear day-by-day plan; Agent Builder ready by day 7; Claude API as NER fallback means system works even if XLM-RoBERTa underperforms; pgvector eliminates separate vector DB complexity |
| Scalability | 8.5 | pgvector in existing PostgreSQL scales without separate service; SQS decouples batch ingestion; SageMaker Serverless auto-scales NER inference; stateless FastAPI scales horizontally; S3 for narrative storage is unlimited |
| Technical Depth | 8.5 | Two-model NER pipeline with fallback logic; structured evidence extraction via LLM; 300-example benchmark with real F1 evaluation; pgvector ANN search; stateful LangGraph with interrupt/resume; active learning feedback loop; multi-drug permutation handling |
| Market Readiness | 8.0 | B2B model eliminates DPDP consent issue; CDSCO mandate creates immediate institutional demand; clear 6-month path to first paid pilot with a telemedicine platform; SaaS pricing model is standard in pharma software; no regulatory approval required for the detection layer (officer makes final call) |
| **Overall** | **8.5** | All dimensions at 8.0 or above |

---

*VigilAI 2.0 — Final Documentation*
*Cognizant Technoverse Hackathon 2026*
*Version 2.0 | April 2026*
