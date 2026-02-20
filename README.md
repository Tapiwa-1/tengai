# Tengai

Monorepo with:

- `backend/`: Flask + SQLAlchemy + RQ + Redis + MySQL-ready API. Product imports/sync use SerpApi (Amazon Product engine).
- `frontend/`: Vue 3 + Vite + TS + Pinia + Router + Tailwind UI.

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
