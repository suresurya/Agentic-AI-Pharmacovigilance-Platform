.PHONY: dev seed test demo install frontend backend

dev:
	cd infra && docker-compose up --build

dev-bg:
	cd infra && docker-compose up --build -d

stop:
	cd infra && docker-compose down

seed:
	cd backend && python -m app.seeds.seed_whoart
	cd backend && python -m app.seeds.seed_demo

test:
	cd backend && pytest tests/ -v
	cd ml && python -m ml.ner.evaluate

demo:
	cd backend && python -m app.seeds.seed_demo

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

install: install-backend install-frontend

frontend:
	cd frontend && npm run dev

backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
