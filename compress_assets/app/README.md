# Compress Assets App

Dark minimal app for asset compression, built with React + TypeScript + Tailwind + shadcn-style components and served by FastAPI.

## Deploy with Docker

From `compress_assets/app` run:

```bash
docker compose up --build -d
```

Then open:

- App: `http://localhost:8000`
- Health check: `http://localhost:8000/api/health`

Stop:

```bash
docker compose down
```

## Local development (without Docker)

### One-command frontend start

```bash
./start.sh
```

`start.sh` automatically:
- installs frontend dependencies (if needed)
- creates `.venv` and installs backend dependencies
- starts FastAPI on `http://localhost:8000`
- starts Vite on `http://localhost:5173` with API wired to backend

### Frontend dev server

```bash
npm install
npm run dev
```

### Backend API server

```bash
pip install -r requirements.txt
uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000
```

The frontend uses `VITE_API_BASE_URL` when provided; otherwise it calls `/api/compress` on the same host.

## Production architecture

- Multi-stage Docker build compiles the React app.
- Final Python image installs `ffmpeg` and serves:
  - static frontend from `dist`
  - API endpoint `POST /api/compress`
- Compression output uses lossless WebP settings to preserve visual quality.
