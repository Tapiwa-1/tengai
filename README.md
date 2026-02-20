# Tengai

Monorepo with:

- `backend/`: Flask + SQLAlchemy + RQ + Redis + SQLite-first API. Agents upload products manually (including pictures) through `/api/v1/agent/import`.
- `frontend/`: Vue 3 + Vite + TS + Pinia + Router + Tailwind UI with an Amazon-inspired storefront.

## Backend quick start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# default DATABASE_URL uses local SQLite file (tengai.db)
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


### Troubleshooting DB connection

If your `DATABASE_URL` is set to MySQL and MySQL is not running, the app will automatically fall back to `sqlite:///tengai.db` during startup so local development can continue.
