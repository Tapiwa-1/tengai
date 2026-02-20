# Tengai

Monorepo with:

- `backend/`: Flask + SQLAlchemy + RQ + Redis + MySQL-ready API. Agents upload products manually (including pictures) through `/api/v1/agent/import`.
- `frontend/`: Vue 3 + Vite + TS + Pinia + Router + Tailwind UI with an Amazon-inspired storefront.

## Backend quick start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Run worker:

```bash
cd backend
python worker.py
```

## Frontend quick start

```bash
cd frontend
npm install
npm run dev
```
