# VigilAI 2.0 — Single-Day Build Plan
### Cognizant Technoverse Hackathon 2026 | April 20, 2026

> **Goal:** Ship a fully working, demo-ready Hinglish pharmacovigilance prototype in one day.
> **Stack:** React + TypeScript · FastAPI · LangGraph · PostgreSQL + pgvector · Claude Sonnet API
> **Team:** Abhiram (Full-Stack) · Varshi (ML/DL #1) · Monika (ML/DL #2) · Surya (Backend)

---

## Overview — Build Sequence

```
PHASE 1 (0h–1h)    → Repo scaffold + environment up
PHASE 2 (1h–3h)    → Database + backend skeleton
PHASE 3 (1h–3h)    → ML pipeline + LangGraph agents     ← parallel with Phase 2
PHASE 4 (3h–5h)    → Frontend components
PHASE 5 (5h–7h)    → Integration — wire everything together
PHASE 6 (7h–8h)    → Dataset + F1 eval + demo prep
PHASE 7 (8h–9h)    → Polish, backup, rehearsal
```

---

## Phase 1 — Scaffold & Environment (0h → 1h)
**All 4 members in parallel. Target: every machine running before any feature work starts.**

### Repository Structure to Create
```
vigilai/
├── frontend/          → Abhiram
├── backend/           → Surya
├── agents/            → Monika
├── ml/                → Varshi
├── data/
│   ├── benchmark/     → train.jsonl (240) + test.jsonl (60)
│   ├── whoart/        → whoart_terms.csv (1,700 entries)
│   └── demo/          → curated_narratives.json (10 inputs)
├── infra/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── .env.example
└── Makefile
```

### Tasks

#### Abhiram — Frontend Init
- [ ] `npm create vite@latest frontend -- --template react-ts`
- [ ] Install: `tailwindcss zustand axios react-router-dom`
- [ ] Create folder structure: `components/layout`, `components/narrative`, `components/pipeline`, `components/evidence`, `components/report`, `components/hitl`
- [ ] Create placeholder files for every component (empty exports)
- [ ] Set up `src/store/` — three Zustand stores: `narrativeStore`, `reportStore`, `pipelineStore`
- [ ] Set up `src/services/api.ts` — Axios instance pointing to `http://localhost:8000`
- [ ] **Done check:** `npm run dev` renders a blank page without errors

#### Surya — Backend Init
- [ ] `mkdir backend && cd backend && python -m venv .venv`
- [ ] Install: `fastapi uvicorn[standard] sqlalchemy alembic asyncpg psycopg2-binary python-jose pydantic[email] python-multipart boto3`
- [ ] Create folder structure: `app/models/`, `app/schemas/`, `app/api/`, `app/websocket/`, `app/services/`
- [ ] Write `docker-compose.yml` — PostgreSQL 16 + pgvector extension + backend service
- [ ] Write `.env.example` with all required keys (DB_URL, ANTHROPIC_API_KEY, JWT_SECRET)
- [ ] **Done check:** `docker-compose up` starts Postgres, `uvicorn app.main:app` starts without errors

#### Varshi — ML Init
- [ ] `mkdir ml && pip install transformers datasets torch seqeval sentence-transformers`
- [ ] Download `xlm-roberta-base` weights to `ml/ner/models/`
- [ ] Download `paraphrase-multilingual-mpnet-base-v2` to `ml/embeddings/models/`
- [ ] Load WHO-ART CSV (1,700 terms) into `data/whoart/whoart_terms.csv`
- [ ] **Done check:** both models load without errors in a test script

#### Monika — Agent Init
- [ ] `mkdir agents && pip install langgraph langchain anthropic`
- [ ] Write `agents/state.py` — `AgentState` TypedDict with all fields:
  ```python
  narrative_id, raw_text, clean_text, language_mix_ratio,
  entities, relations, normalized_pairs, report_id, hitl_required, hitl_candidates
  ```
- [ ] Write `agents/graph.py` — wire 6 empty node stubs: Ingest → Preprocess → NER → Relation → Normalize → Report
- [ ] **Done check:** `python agents/graph.py` compiles and runs with dummy input

---

## Phase 2 — Database + Backend (1h → 3h)
**Owner: Surya (primary) · Varshi (WHO-ART embeddings)**

### 2A — SQLAlchemy Models

#### File: `backend/app/models/narrative.py`
```python
# Table: narratives
# Columns: id (UUID PK), source_text (TEXT), source_type (ENUM),
#          customer_id (UUID), language_mix_ratio (FLOAT),
#          status (ENUM: queued/processing/pending_review/done/failed),
#          created_at (TIMESTAMPTZ)
```

#### File: `backend/app/models/entity.py`
```python
# Table: entities
# Columns: id, narrative_id (FK), entity_text, entity_type (ENUM: drug/symptom/dosage),
#          char_start, char_end, confidence, source_model
```

#### File: `backend/app/models/adr_report.py`
```python
# Table: adr_reports
# Columns: id, narrative_id (FK), drug_entity_id (FK), symptom_entity_id (FK),
#          relation_type (ENUM: Causes-ADR/Possible-ADR),
#          confidence, evidence (JSONB), normalized_term, whoart_code,
#          officer_status (ENUM: pending/approved/rejected/modified),
#          officer_notes, created_at
```

#### File: `backend/app/models/officer_action.py`
```python
# Table: officer_actions
# Columns: id, report_id (FK), action_type (ENUM),
#          original_value (JSONB), corrected_value (JSONB),
#          officer_id, created_at
```

#### File: `backend/app/models/whoart_term.py`
```python
# Table: whoart_terms (pgvector)
# Columns: id (INT PK), code, term, system_organ_class,
#          embedding VECTOR(768)
```

### Tasks
- [ ] Write all 5 SQLAlchemy models
- [ ] Configure Alembic, run `alembic init` and `alembic revision --autogenerate`
- [ ] Run `alembic upgrade head` — all tables created
- [ ] Write `backend/app/seeds/seed_whoart.py` — reads CSV, inserts 1,700 rows
- [ ] Run seed script → confirm rows in DB

### 2B — Pydantic v2 Schemas (`backend/app/schemas/`)

- [ ] `narrative.py` — `NarrativeCreate`, `NarrativeResponse`, `NarrativeStatus`
- [ ] `entity.py` — `EntityOut` (text, type, start, end, confidence, source_model)
- [ ] `report.py` — `ReportOut`, `ReportReviewRequest`, `EvidenceObject`
- [ ] `websocket.py` — `WSNodeComplete`, `WSHITLRequired`
- [ ] `hitl.py` — `HITLCandidate`, `HITLResolveRequest`

### 2C — REST API Endpoints (`backend/app/api/`)

#### `narratives.py`
- [ ] `POST /api/v1/narratives/` — validate payload, write to DB (status=queued), trigger `pipeline_runner.run_async(narrative_id)`
- [ ] `GET /api/v1/narratives/{id}/` — return narrative + status

#### `reports.py`
- [ ] `GET /api/v1/reports/` — list with filters (status, drug, date range)
- [ ] `GET /api/v1/reports/{id}/` — full report with evidence object
- [ ] `PATCH /api/v1/reports/{id}/review/` — approve/reject/modify; write to `officer_actions`
- [ ] `GET /api/v1/reports/{id}/export/` — return full JSON blob
- [ ] `GET /api/v1/reports/analytics/` — counts by drug, date, status

#### `hitl.py`
- [ ] `POST /api/v1/reports/{id}/resolve-hitl/` — receive officer WHO-ART selection, call `graph.resume()`

#### `whoart.py`
- [ ] `GET /api/v1/whoart/search/?q=` — text search across `whoart_terms` table

### 2D — WebSocket (`backend/app/websocket/manager.py`)
- [ ] `ConnectionManager` class — connect, disconnect, `send_to_narrative(narrative_id, event)`
- [ ] `WS /ws/pipeline/{narrative_id}` endpoint — officer subscribes on narrative submit

### 2E — Auth Middleware
- [ ] Simple JWT middleware — hardcoded demo officer credentials for prototype
- [ ] `GET /api/v1/auth/token` — returns JWT for demo login

---

## Phase 3 — ML Pipeline + LangGraph Agents (1h → 3h)
**Parallel with Phase 2. Owners: Varshi (NER + embeddings) · Monika (LangGraph nodes)**

### 3A — Hinglish Preprocessing (`ml/preprocessing/hinglish_cleaner.py`)
- [ ] Unicode normalization (Devanagari → Roman if needed)
- [ ] Noise removal: hashtags, URLs, emojis, repeated characters
- [ ] Language mix ratio calculation: count Hindi tokens vs English tokens
- [ ] HuggingFace BPE tokenization via `xlm-roberta-base` tokenizer
- [ ] **Output:** `clean_text: str`, `tokens: list[str]`, `language_mix_ratio: float`

### 3B — BIO Tag Converter (`ml/ner/bio_converter.py`)
- [ ] Read JSONL benchmark format
- [ ] Convert entity span annotations to BIO tags (`B-DRUG`, `I-DRUG`, `B-SYMPTOM`, etc.)
- [ ] Output HuggingFace `datasets.Dataset` format
- [ ] **Used for:** XLM-RoBERTa fine-tuning

### 3C — NER Model (`ml/ner/model.py` + `ml/ner/train.py`)
- [ ] Load `xlm-roberta-base` with token classification head (5 labels: O, B-DRUG, I-DRUG, B-SYMPTOM, I-SYMPTOM)
- [ ] Training config: 3 epochs, lr=2e-5, batch_size=16, seqeval F1 metric
- [ ] Save best checkpoint to `ml/ner/models/finetuned/`
- [ ] Inference function: `predict_entities(text: str) → list[EntitySpan]`
  - Returns: `[{text, type, char_start, char_end, confidence}]`

### 3D — Claude Sonnet NER Fallback (`ml/ner/claude_fallback.py`)
- [ ] Structured JSON prompt requesting entity list with spans
- [ ] Triggered when XLM-RoBERTa confidence < 0.70
- [ ] Parse Claude's JSON response into same `EntitySpan` format
- [ ] Tag `source_model = "claude-sonnet"`

### 3E — WHO-ART Embedding Index (`ml/embeddings/whoart_embedder.py`)
- [ ] Load `paraphrase-multilingual-mpnet-base-v2`
- [ ] Batch-encode all 1,700 WHO-ART terms → 768-dim vectors
- [ ] Insert vectors into `whoart_terms.embedding` via pgvector
- [ ] `similarity_search(symptom_text: str, top_k=3) → list[WHOARTCandidate]`
  - Uses pgvector cosine similarity: `embedding <=> query_vec`

### 3F — LangGraph Nodes (`agents/nodes/`)

#### `ingest.py`
```python
# Input: raw narrative text + metadata
# Actions:
#   - Validate payload (Pydantic)
#   - Detect language mix ratio
#   - Write to DB with status='queued'
#   - Initialize state
# Output: state with narrative_id, raw_text, language_mix_ratio
```
- [ ] Implement ingest node

#### `preprocess.py`
```python
# Input: raw_text from state
# Actions:
#   - Call hinglish_cleaner.clean(raw_text)
#   - Tokenize
#   - Update DB status='processing'
# Output: state with clean_text, tokens
```
- [ ] Implement preprocess node

#### `ner.py`
```python
# Input: clean_text
# Actions:
#   - Run XLM-RoBERTa inference
#   - If any entity confidence < 0.70 → run Claude fallback for that span
#   - Write entities to DB
#   - Emit WS event: node_complete(NER)
# Output: state with entities list
```
- [ ] Implement NER node with fallback logic

#### `relation.py`
```python
# Input: clean_text, entities
# Actions:
#   - For every (DRUG, SYMPTOM) permutation, call Claude Sonnet 6-shot prompt
#   - Parse evidence JSON: relation_type, confidence, temporal_marker,
#     temporal_marker_translation, negation_detected, causal_pattern, plain_language_reason
#   - Filter: keep only Causes-ADR and Possible-ADR
#   - Rank by confidence
#   - Emit WS event: node_complete(Relation)
# Output: state with relations list (each has full evidence object)
```
- [ ] Implement relation + explainability node

**Claude Sonnet Prompt Template (6-shot, to use in relation.py):**
```
You are a pharmacovigilance expert. Analyze this Hinglish patient narrative.

Narrative: {clean_text}
Drug entity: {drug_span}
Symptom entity: {symptom_span}

Classify as exactly one of: Causes-ADR, Treats-Indication, No-Relation

Extract evidence:
- temporal_marker: time-indicating phrase (e.g. "ke baad", "baad mein") or null
- temporal_marker_translation: English translation or null
- negation_detected: true/false (check "nahi", "nahin", "no", "not")
- causal_pattern: one of [temporal_proximity_post_ingestion, patient_self_attribution,
  concurrent_occurrence, negative_association, no_clear_pattern]
- plain_language_reason: one English sentence explaining classification

Respond ONLY in this exact JSON:
{"relation_type":"...","confidence":0.0,"temporal_marker":"...","temporal_marker_translation":"...","negation_detected":false,"causal_pattern":"...","plain_language_reason":"..."}
```

#### `normalize.py`
```python
# Input: relations (each with symptom span)
# Actions:
#   - Embed symptom text
#   - pgvector top-3 cosine similarity search
#   - If top score > 0.82: auto-select, continue
#   - If top score ≤ 0.82: graph.interrupt() — emit WS hitl_required event
#     with 3 candidates + scores
#   - On resume: accept officer_selection, log to officer_actions
# Output: state with normalized_term, whoart_code per pair
```
- [ ] Implement normalize node with `graph.interrupt()` / `graph.resume()`

#### `report.py`
```python
# Input: full state
# Actions:
#   - Assemble ADR report object
#   - Write to adr_reports (one row per retained pair)
#   - Update narrative status='pending_review'
#   - Emit WS node_complete(Report) event
# Output: state with report_id
```
- [ ] Implement report node

### 3G — Wire the Graph (`agents/graph.py`)
- [ ] Define `StateGraph(AgentState)`
- [ ] Add all 6 nodes
- [ ] Add edges: linear Ingest → Preprocess → NER → Relation → Normalize → Report
- [ ] Add conditional edge at Normalize: if `hitl_required` → interrupt, else continue
- [ ] Compile with `graph.compile(checkpointer=MemorySaver())`
- [ ] Test: `graph.invoke({"raw_text": "Maine metformin li aur ulti hui"}, config={"thread_id": "test-1"})`

---

## Phase 4 — Frontend Components (3h → 5h)
**Owner: Abhiram**

### 4A — Layout (`src/components/layout/`)

#### `MainLayout.tsx`
- [ ] Three-column layout: Sidebar (left) · Main Content (center) · Evidence Panel (right)
- [ ] Responsive: evidence panel collapses on smaller screens

#### `Sidebar.tsx`
- [ ] Nav links: Dashboard · Reports · Batch Upload · Analytics
- [ ] Active link highlighting
- [ ] Demo mode badge

#### `Header.tsx`
- [ ] VigilAI logo + title
- [ ] Officer name display (from JWT)
- [ ] Logout button

### 4B — Narrative Input (`src/components/narrative/`)

#### `NarrativeInput.tsx`
- [ ] Textarea for Hinglish text (placeholder with example narrative)
- [ ] Submit button with loading spinner state
- [ ] Language mix ratio badge (shown after submit)
- [ ] Character count display
- [ ] On submit: `POST /api/v1/narratives/` → store narrative_id → open WebSocket

#### `EntityHighlighter.tsx`
- [ ] Takes `source_text: string` + `entities: Entity[]`
- [ ] Renders text with colored inline spans:
  - DRUG → blue highlight
  - SYMPTOM → orange highlight
  - DOSAGE → green highlight
- [ ] Tooltip on hover showing entity type + confidence %

#### `BatchUpload.tsx`
- [ ] CSV drag-and-drop zone
- [ ] File validation (CSV only, max 1MB for prototype)
- [ ] On upload: `POST /api/v1/narratives/batch/` → show job_id
- [ ] Progress list showing per-narrative status

### 4C — Pipeline Progress (`src/components/pipeline/`)

#### `PipelineProgress.tsx`
- [ ] Six node cards in sequence: Ingest → Preprocess → NER → Relation → Normalize → Report
- [ ] States: waiting (grey) · running (blue pulse) · complete (green) · error (red)
- [ ] Driven by WebSocket events from `pipelineStore`

#### `NodeStatus.tsx`
- [ ] Node name + icon
- [ ] Status dot with animation
- [ ] Output preview text (e.g. "Found: metformin (DRUG), nausea (SYMPTOM)")

### 4D — Evidence Panel (`src/components/evidence/`)

#### `EvidencePanel.tsx`
- [ ] Drug entity box (blue) + Symptom entity box (orange) side by side
- [ ] Confidence % badge on each
- [ ] Relation type badge (Causes-ADR / Possible-ADR) with confidence bar
- [ ] WHO-ART term + code display
- [ ] Evidence details section:
  - Temporal marker + translation
  - Causal pattern (human-readable label)
  - Negation check result
  - Plain-language reason paragraph

#### `ConfidenceBar.tsx`
- [ ] Horizontal bar, width = confidence %
- [ ] Color: green (>0.80) · yellow (0.60–0.80) · red (<0.60)
- [ ] Numeric label on right

### 4E — Report Components (`src/components/report/`)

#### `ReportCard.tsx`
- [ ] Drug → Symptom header with arrow
- [ ] Confidence bar
- [ ] WHO-ART term chip
- [ ] Status badge (pending / approved / rejected / modified)
- [ ] "View Evidence" expand toggle
- [ ] Approve / Reject / Modify action buttons
- [ ] On approve: `PATCH /api/v1/reports/{id}/review/` with `{action: "approve"}`

#### `ReportsList.tsx`
- [ ] Filter bar: status dropdown · drug search · date range picker
- [ ] Sorted list of `ReportCard` components
- [ ] Empty state when no reports
- [ ] Pagination (10 per page)

#### `ReportDetail.tsx`
- [ ] Full report view: source narrative + entity highlights + evidence panel
- [ ] Multi-drug ranking list (if polypharmacy narrative)
- [ ] Export JSON button → `GET /api/v1/reports/{id}/export/`
- [ ] Audit trail section (officer actions history)

### 4F — HITL Prompt (`src/components/hitl/`)

#### `HITLPrompt.tsx`
- [ ] Modal overlay triggered when `pipelineStore.hitlRequired === true`
- [ ] Header: "Officer Action Required — Confidence below threshold"
- [ ] Shows original symptom text
- [ ] Three `CandidateCard` components with rank, term, code, similarity score
- [ ] Click-to-select — highlights selected candidate
- [ ] Confirm button → `POST /api/v1/reports/{id}/resolve-hitl/`
- [ ] On resolve: WebSocket receives resume event, pipeline continues

#### `CandidateCard.tsx`
- [ ] WHO-ART code badge
- [ ] Term name (large)
- [ ] System organ class (subtitle)
- [ ] Similarity score bar
- [ ] Selected state (blue border)

### 4G — Zustand Stores (`src/store/`)

#### `narrativeStore.ts`
```typescript
// State: currentNarrativeId, status, submitting
// Actions: submitNarrative(), setStatus()
```

#### `reportStore.ts`
```typescript
// State: reports[], selectedReportId, filters
// Actions: fetchReports(), reviewReport(), exportReport()
```

#### `pipelineStore.ts`
```typescript
// State: nodes (6 node statuses), hitlRequired, hitlCandidates
// Actions: updateNodeStatus(), setHITLRequired(), resolveHITL()
// WebSocket listener: parse incoming WS events and update state
```

### 4H — WebSocket Client (`src/services/websocket.ts`)
- [ ] `connectPipeline(narrativeId)` — open WS to `/ws/pipeline/{id}`
- [ ] Parse `node_complete` events → update `pipelineStore` node status
- [ ] Parse `hitl_required` events → set `pipelineStore.hitlRequired = true` with candidates
- [ ] Auto-reconnect on disconnect

---

## Phase 5 — Integration (5h → 7h)
**All 4 members. This is the critical wiring phase.**

### 5A — Backend ↔ Agent Bridge (`backend/app/services/pipeline_runner.py`)
- [ ] `run_async(narrative_id: str)` — loads narrative from DB, calls `graph.invoke()`
- [ ] Passes `ws_manager` reference so nodes can emit WebSocket events
- [ ] Handles `graph.interrupt()` — stores checkpoint, emits `hitl_required` WS event
- [ ] `resume(narrative_id: str, hitl_selection: dict)` — calls `graph.resume()` with selection

### 5B — HITL Flow End-to-End
- [ ] Narrative hits Normalize node with low confidence
- [ ] `graph.interrupt()` fires
- [ ] `pipeline_runner` catches interrupt, emits `hitl_required` WS event with 3 candidates
- [ ] Frontend `HITLPrompt` modal appears with candidates
- [ ] Officer clicks a candidate → `POST /api/v1/reports/{id}/resolve-hitl/`
- [ ] Backend calls `graph.resume()` → pipeline finishes → Report node runs
- [ ] Frontend receives `node_complete(Report)` → closes modal → shows report
- [ ] **Full test:** verify this works on at least 2 narratives

### 5C — Multi-Drug Narrative Flow
- [ ] Submit narrative with 2 drugs mentioned
- [ ] Relation node produces ranked pair list
- [ ] Two `ReportCard` items appear in `ReportsList`
- [ ] Evidence panel shows separate evidence for each pair
- [ ] Officer can approve/reject each pair independently

### 5D — Batch Upload Flow
- [ ] Upload a CSV with 5 test narratives
- [ ] Backend queues all 5 via `asyncio.Queue`
- [ ] Each processes sequentially through the pipeline
- [ ] Batch status page shows real-time per-narrative progress
- [ ] All 5 reports appear in `ReportsList` when done

### 5E — Integration Test Checklist
Run each scenario and confirm it works end-to-end:

| Scenario | Expected Result |
|---|---|
| Single Hinglish ADR narrative | ADR report with evidence, WHO-ART term |
| Narrative with 2 drugs | 2 ranked report pairs |
| Negated symptom ("chakkar nahi aaya") | No ADR report generated |
| Indication-only narrative | No Causes-ADR pair in output |
| Low-confidence normalization | HITL modal fires, officer selects, pipeline resumes |
| Officer approves report | Status flips to approved, logged to officer_actions |
| Officer rejects report | Status flips to rejected |
| Batch CSV upload (5 rows) | All 5 reports generated |
| JSON export | Downloads valid JSON with evidence |

---

## Phase 6 — Dataset + F1 Evaluation (7h → 8h)
**Owners: Varshi (evaluation) · all 4 members for dataset writing**

### 6A — Benchmark Dataset (`data/benchmark/`)

**Distribution to write (300 examples total):**

| Category | Count | Example pattern |
|---|---|---|
| Single-drug ADR (positive) | 90 | Drug + temporal marker + symptom |
| Multi-drug ADR (positive) | 60 | 2+ drugs, one causes ADR |
| Ambiguous (low confidence) | 30 | No clear temporal cue |
| Indication-only (negative) | 60 | Drug used to treat pre-existing condition |
| No medical content (negative) | 30 | General health talk, no ADR |
| Negated symptom (negative) | 30 | "chakkar nahi aaya" patterns |

**Common Hinglish patterns to use:**

Temporal markers: `lene ke baad`, `khane ke baad`, `pine ke baad`, `use karne ke baad`, `baad mein`, `phir se`

ADR descriptions: `chakkar aana`, `ulti/nausea`, `pet dard`, `sar dard`, `neend na aana`, `kamzori`, `haath kaanpna`, `dil ki dhadkan`, `rash`, `khujli`, `sujan`

Drugs: `paracetamol`, `metformin`, `amlodipine`, `atorvastatin`, `pantoprazole`, `amoxicillin`, `ibuprofen`, `aspirin`, `metoprolol`, `omeprazole`

**JSONL format per example:**
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

- [ ] Write 75 examples per person → merge into `data/benchmark/raw_combined.jsonl`
- [ ] Cross-review: each person validates 25 examples from one other member
- [ ] Split: first 240 → `train.jsonl`, last 60 → `test.jsonl`

### 6B — XLM-RoBERTa Fine-Tuning (`ml/ner/train.py`)
- [ ] Load `train.jsonl` → convert to BIO tags via `bio_converter.py`
- [ ] Fine-tune for 3 epochs (5 if time permits), eval every 50 steps
- [ ] Save best checkpoint (highest validation F1)
- [ ] Load checkpoint into NER node

### 6C — F1 Evaluation (`ml/ner/evaluate.py`)
Run on `test.jsonl` (60 examples):
- [ ] Drug NER F1 (expected: 0.78–0.82)
- [ ] Symptom NER F1 (expected: 0.65–0.72)
- [ ] Relation extraction F1 (expected: 0.70–0.76)
- [ ] WHO-ART Top-1 accuracy (expected: 0.72–0.78)
- [ ] WHO-ART Top-3 accuracy (expected: 0.88–0.92)
- [ ] Print and save results to `data/benchmark/f1_results.txt`
- [ ] **Print the results sheet** — bring physical copy to demo

---

## Phase 7 — Polish, Backup & Demo Prep (8h → 9h)
**All 4 members**

### 7A — UI Polish (Abhiram)
- [ ] Loading skeletons on `ReportsList` while fetching
- [ ] Error toast on API failures
- [ ] Empty state on `ReportsList` when no reports yet
- [ ] Smooth CSS transitions on pipeline node status changes
- [ ] Demo mode toggle — preloads 10 curated narratives instantly

### 7B — 10 Curated Demo Narratives (`data/demo/curated_narratives.json`)
Create JSON file with 10 pre-chosen narratives that together showcase every system feature:

| # | Narrative | Feature Demonstrated |
|---|---|---|
| 1 | Single drug, clear temporal marker | Basic ADR extraction + evidence panel |
| 2 | Two drugs, one causes ADR | Multi-drug ranking |
| 3 | Three drugs, ambiguous | Polypharmacy complexity |
| 4 | Negated symptom | Negation detection |
| 5 | Indication-only (no ADR) | True negative |
| 6 | Low WHO-ART confidence | HITL pause/resume |
| 7 | Dosage + ADR combined | DOSAGE entity extraction |
| 8 | Hindi-heavy Hinglish | Language mix handling |
| 9 | English-heavy Hinglish | Code-mixed input |
| 10 | Multi-symptom, multi-drug | Full system complexity |

### 7C — Docker Compose Final (`infra/docker-compose.yml`)
- [ ] Services: `postgres` (with pgvector), `backend` (FastAPI), `frontend` (Vite dev server)
- [ ] `backend` depends_on `postgres`
- [ ] Volume: `postgres_data` persists between restarts
- [ ] `make dev` runs `docker-compose up --build`
- [ ] `make seed` runs WHO-ART seed + demo data seed
- [ ] Test: fresh `docker-compose up` from clean state → all services healthy

### 7D — Offline Backup (Monika)
- [ ] Cache LangGraph output for all 10 demo narratives as static JSON
- [ ] Dashboard offline mode: if API unreachable → load from `data/demo/cached_outputs.json`
- [ ] Local SQLite fallback if PostgreSQL is unreachable
- [ ] Test offline mode works: shut down backend, reload dashboard

### 7E — Demo Rehearsal (All 4 members — 30 min timed)

#### 5-Minute Demo Script

**Minute 1 — The Problem (spoken):**
> "Every pharmaceutical company in India is legally required by CDSCO to report Adverse Drug Reactions. Most patient feedback arrives in Hinglish — a mix of Hindi and English. No software anywhere can process it. VigilAI is the first."

**Minute 2 — Single Narrative Live Demo:**
- Input narrative #1 from curated list
- Point to: 6 pipeline nodes lighting up in sequence on the right
- Point to: Colored entity highlights in the source text
- Point to: Evidence panel — *"Notice the temporal marker 'lene ke baad' — the system identifies this as causal. This is why the officer can trust the classification."*

**Minute 3 — Multi-Drug Narrative:**
- Input narrative #2 (two drugs)
- Show: Two report pairs ranked by confidence
- Say: *"Real patients take multiple medications. VigilAI handles the full complexity."*

**Minute 4 — HITL Checkpoint:**
- Input narrative #6 (low WHO-ART confidence)
- Show: Pipeline pauses at Normalize node
- Show: HITL modal with 3 WHO-ART candidates + similarity scores
- Officer clicks candidate 1 → pipeline resumes → report generated
- Say: *"This is not a review form. The AI genuinely waits. Nothing becomes a report without human validation."*

**Minute 5 — Benchmark Results + Close:**
- Show printed F1 results sheet
- Say: *"Our NER achieves F1 of [X] on a 60-example held-out test set from the first publicly available labeled Hinglish ADR benchmark — which we created as part of this project and are open-sourcing today."*
- Close: *"3,000 pharmaceutical manufacturers in India have a CDSCO mandate and no tool that speaks their patients' language. VigilAI does."*

---

## Implementation Priority Order
If time runs short, cut in this order (bottom = cut first):

| Priority | Feature | Impact if cut |
|---|---|---|
| P0 — Must ship | NER node (Claude fallback) + Relation node + Evidence JSON | Demo breaks entirely |
| P0 — Must ship | EntityHighlighter + EvidencePanel + ReportCard | Nothing to show |
| P0 — Must ship | PipelineProgress WebSocket | Demo looks dead |
| P0 — Must ship | HITL modal + graph.interrupt()/resume() | Key differentiator gone |
| P1 — Ship if possible | Fine-tuned XLM-RoBERTa (can use Claude-only fallback) | F1 numbers unavailable |
| P1 — Ship if possible | Batch CSV upload | Nice-to-have for demo |
| P2 — Nice to have | Analytics dashboard | Skippable in demo |
| P2 — Nice to have | JWT auth (use hardcoded officer) | Prototype can skip |
| P3 — Cut if needed | Devanagari script detection | Not visible in demo |
| P3 — Cut if needed | Full Docker Compose | Can run services manually |

---

## Environment Variables (`.env.example`)
```env
# Database
DATABASE_URL=postgresql+asyncpg://vigilai:vigilai@localhost:5432/vigilai
POSTGRES_USER=vigilai
POSTGRES_PASSWORD=vigilai
POSTGRES_DB=vigilai

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Auth
JWT_SECRET=your-secret-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480

# Demo officer credentials
DEMO_OFFICER_EMAIL=officer@vigilai.demo
DEMO_OFFICER_PASSWORD=demo2026

# Frontend
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

---

## Key Technical Decisions

| Decision | Choice | Reason |
|---|---|---|
| LLM for relation extraction | Claude Sonnet (`claude-sonnet-4-6`) | Best structured JSON output, Hinglish understanding |
| NER primary model | XLM-RoBERTa-base fine-tuned | Multilingual, handles code-mixed Roman script |
| NER fallback | Claude Sonnet | Ensures pipeline never fails on low-confidence inputs |
| Vector search | pgvector in PostgreSQL | No separate vector DB, sub-10ms similarity search |
| Agent framework | LangGraph | Only framework with real graph.interrupt()/resume() for HITL |
| Async queue (prototype) | asyncio.Queue | No AWS SQS needed locally — same behavior |
| State persistence (HITL) | LangGraph MemorySaver | Persists graph state across interrupt/resume cycles |
| Frontend state | Zustand | Lightweight, no Redux boilerplate |

---

## Done Criteria — Ship Checklist

Before demo, confirm every item is green:

- [ ] Submit a Hinglish narrative → entities highlighted in dashboard within 10 seconds
- [ ] Evidence panel shows temporal marker, causal pattern, plain-language reason
- [ ] Submit narrative with 2 drugs → 2 ranked report cards appear
- [ ] Low-confidence normalization → HITL modal fires → officer selects → report generated
- [ ] Officer approves a report → status flips to approved → logged in officer_actions
- [ ] Batch CSV (5 rows) → all 5 reports generated
- [ ] JSON export downloads valid file with full evidence object
- [ ] Negated symptom narrative → no ADR report generated
- [ ] Pipeline progress sidebar shows all 6 nodes completing in sequence
- [ ] F1 results sheet has real numbers from real evaluation
- [ ] `docker-compose up` from clean state → all services healthy
- [ ] Offline backup mode loads cached results when API is down
- [ ] Full 5-minute demo rehearsed and timed

---

*VigilAI 2.0 · Cognizant Technoverse Hackathon 2026 · Single-Day Build Plan*
*Last updated: April 20, 2026*
