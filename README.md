# Tengai Shop (Vue + Express + SQLite)

This project uses:
- **Vue 3 + Vite** for the frontend (`frontend/`)
- **Express + SQLite** for the backend API (`server.js`)

## Run with Yarn

### 1) Install dependencies

```bash
yarn install
```

### 2) Run backend (Express API)

From the project root:

```bash
yarn start
```

Backend runs at `http://localhost:3000`.

### 3) Run frontend dev server (Vue + Vite)

You can run frontend in either way:

From project root:

```bash
yarn dev:client
```

Or from `frontend/` directly:

```bash
cd frontend
yarn dev
```

Frontend runs at `http://localhost:5173` and proxies `/api` requests to the backend.

### 4) Build frontend for production

From project root:

```bash
yarn build:client
```

Or from `frontend/`:

```bash
cd frontend
yarn build
```

Then run backend from root:

```bash
yarn start
```

Express will serve built files from `frontend/dist`.

## Port already in use (`EADDRINUSE`)

If you see `EADDRINUSE: address already in use :::3000`, another process is already running on port `3000`.

Use one of these:

```bash
# stop the existing process using port 3000
# then start again
yarn start

# OR run backend on a different port
PORT=3001 yarn start
```

(Windows PowerShell)

```powershell
$env:PORT=3001; yarn start
```

## Helpful scripts

- `yarn lint` – syntax check for server/client entry files
- `yarn preview:client` – preview built frontend

## Windows/Corepack note

If you want to use modern Yarn via Corepack, run:

```powershell
corepack enable
corepack prepare yarn@stable --activate
```

This project does **not** require a pinned Yarn version, so Yarn Classic (`1.x`) also works.
