# VigilAI 2.0 — Quick Start

## Prerequisites
- Docker Desktop running
- Python 3.11+
- Node.js 18+
- Anthropic API key

## Step 1 — Set API Key
Edit `backend/.env` and replace `your-anthropic-api-key-here` with your real key.

## Step 2 — Start PostgreSQL
```bash
cd infra
docker-compose up postgres -d
```
Wait ~10 seconds for postgres to be healthy.

## Step 3 — Install + Seed Backend
```bash
cd backend
pip install -r requirements.txt
python -m app.seeds.seed_whoart
python -m app.seeds.seed_demo
```

## Step 4 — Start Backend
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API docs available at: http://localhost:8000/docs

## Step 5 — Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Dashboard at: http://localhost:5173

## Step 6 — Login
- Email: `officer@vigilai.demo`
- Password: `demo2026`

## Step 7 — Demo
1. Go to http://localhost:5173
2. Click **Demo 1** in the narrative input
3. Click **Analyse Narrative**
4. Watch the 6 pipeline nodes light up in sequence
5. See entity highlighting and evidence panel appear
6. Click **Demo 6** to trigger the HITL checkpoint

## Docker All-in-One (alternative)
```bash
cd infra
docker-compose up --build
```

## Test the pipeline directly
```bash
cd agents
python graph.py
```
