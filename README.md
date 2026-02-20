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

```bash
yarn start
```

Backend runs at `http://localhost:3000`.

### 3) Run frontend dev server (Vue + Vite)

In another terminal:

```bash
yarn dev:client
```

Frontend runs at `http://localhost:5173` and proxies `/api` requests to the backend.

### 4) Build frontend for production

```bash
yarn build:client
```

Then run the backend:

```bash
yarn start
```

Express will serve built files from `frontend/dist`.

## Helpful scripts

- `yarn lint` – syntax check for server/client entry files
- `yarn preview:client` – preview built frontend

## Windows/Corepack note

If you want to use modern Yarn via Corepack, run:

```powershell
corepack enable
corepack prepare yarn@stable --activate
```

But this project no longer requires a pinned Yarn version, so Yarn Classic (`1.x`) also works.
