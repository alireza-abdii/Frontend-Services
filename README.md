# Frontend Tools Platform

A microfrontend-style workspace for internal frontend asset utilities. One **core landing** app hosts two independent tool services in tabs. Each service ships its own React UI and FastAPI backend, and can be built and deployed as a separate Docker image.

## Overview

| Service | Purpose | Default port |
|--------|---------|--------------|
| **frontend-core-service** | Tabbed shell / landing page | `8200` |
| **compress_assets** | Image compression (PNG, JPG, WEBP, SVG) | `8000` |
| **image_to_component** | SVG → reusable React component (TSX/JSX) | `8100` |

**Recommended entry point:** open the core landing at `http://localhost:8200` (or your server host on port `8200`). Tool URLs are resolved from the browser host, so the same setup works on localhost and remote servers without hardcoded paths.

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│  frontend-core-service (React + FastAPI)                      │
│  Port 8200 — tabs embed tool UIs in iframes                 │
└───────────────┬─────────────────────────┬─────────────────────┘
                │                         │
                ▼                         ▼
┌───────────────────────────┐ ┌───────────────────────────────┐
│  compress_assets          │ │  image_to_component           │
│  React + FastAPI          │ │  React + FastAPI              │
│  Port 8000                │ │  Port 8100                    │
│  ffmpeg image pipeline    │ │  SVG → TSX/JSX components    │
└───────────────────────────┘ └───────────────────────────────┘
```

- **Pattern:** three deployable units; shared UX conventions (dark theme, Tailwind, shadcn-style components).
- **Integration:** core loads `http://<host>:8000` and `http://<host>:8100` in iframes.
- **Backends:** Python 3 + FastAPI; compression uses **ffmpeg**.

## Repository structure

```text
.
├── README.md                      # This file
├── docker-compose.services.yml    # Run all services together
├── run.sh                         # Helper: up / down / rebuild / logs / ps
├── compress_assets/
│   ├── optimize_svg_to_webp.py  # Standalone CLI for SVG/image optimization
│   ├── compress.py                # Legacy scripts (reference)
│   └── app/                       # Service app (UI + API + Docker)
├── image_to_component/
│   └── app/
└── frontend-core-service/
    └── app/
```

Each service lives under `<service>/app/` with:

- `src/` — React + TypeScript + Tailwind UI  
- `backend_api.py` — FastAPI API and static file serving for production builds  
- `start.sh` — local dev (installs deps, starts API + Vite)  
- `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `package.json`

## Quick start (Docker, all services)

From the repository root:

```bash
git clone <your-repo-url>
cd <repo-folder>
chmod +x run.sh
./run.sh rebuild
```

Open **http://localhost:8200**.

### `run.sh` commands

| Command | Description |
|---------|-------------|
| `./run.sh up` | Start all containers (no rebuild) |
| `./run.sh rebuild` | Build images and start |
| `./run.sh down` | Stop and remove containers |
| `./run.sh ps` | Show container status |
| `./run.sh logs` | Follow combined logs |

### Docker Compose (without `run.sh`)

```bash
docker compose -f docker-compose.services.yml up --build -d
# or, on older setups:
docker-compose -f docker-compose.services.yml up --build -d
```

Image tags (see `docker-compose.services.yml`):

- `services/compress-assets:front-tools`
- `services/image-to-component:front-tools`
- `services/frontend-core-service:front-tools`

## Production deployment (prebuilt images)

Build or export images on a build machine, transfer to the server, then load and run without rebuilding.

**Export (build machine):**

```bash
docker save -o front-tools_bundle.tar \
  services/compress-assets:front-tools \
  services/image-to-component:front-tools \
  services/frontend-core-service:front-tools
```

**Deploy (server):**

```bash
docker load -i front-tools_bundle.tar
docker compose -f docker-compose.services.yml up -d --no-build
# or: docker-compose -f docker-compose.services.yml up -d --no-build
```

Open **http://<server-host>:8200**. Ensure firewall rules allow **8200** (and **8000** / **8100** if you need direct access to tool UIs).

## Local development (without Docker)

Each service can run on its own. For the full tabbed experience, start all three (three terminals or use Docker).

### 1. Compress Assets

```bash
cd compress_assets/app
chmod +x start.sh
./start.sh
```

- API: **http://localhost:8000**  
- Vite dev UI: usually **http://localhost:5173** (or next free port)  
- Requires **ffmpeg** on the host (see [System requirements](#system-requirements)).

**Standalone Python CLI** (batch files, no UI):

```bash
cd compress_assets
python3 optimize_svg_to_webp.py
```

### 2. Image To Component

```bash
cd image_to_component/app
chmod +x start.sh
./start.sh
```

- API: **http://localhost:8100**  
- Vite dev UI: **http://localhost:5175**  
- Converts **SVG** files to TSX/JSX React components (path-based SVG output).

### 3. Frontend Core (landing only)

```bash
cd frontend-core-service/app
chmod +x start.sh
./start.sh
```

- API + built/served UI: **http://localhost:8200**  
- Vite dev: **http://localhost:5176**  
- Tabs need compress and image-to-component services running on **8000** and **8100**.

### Manual local stack (all three)

| Terminal | Directory | Command |
|----------|-----------|---------|
| 1 | `compress_assets/app` | `./start.sh` |
| 2 | `image_to_component/app` | `./start.sh` |
| 3 | `frontend-core-service/app` | `./start.sh` |

Then open **http://localhost:8200** (or the core dev port from terminal 3).

## Run a single service with Docker

From each service’s `app` directory:

```bash
# Compress Assets
cd compress_assets/app
docker compose up --build -d

# Image To Component
cd image_to_component/app
docker compose up --build -d

# Core landing only
cd frontend-core-service/app
docker compose up --build -d
```

Published ports match the table in [Overview](#overview).

## Service details

### Compress Assets

- Upload PNG, JPG, JPEG, WEBP, or SVG.  
- Raster images → optimized **WebP**.  
- SVG with embedded base64 images → optimized SVG (embedded images converted to WebP where possible).  
- Drag-and-drop upload, progress UI, download of result.

### Image To Component

- Upload **SVG** icons.  
- Output: reusable React component as **TSX** or **JSX**.  
- Preserves SVG structure (`<svg>`, `<path>`, groups, defs, etc.).

### Frontend Core Service

- Single landing with tabs for both tools.  
- Responsive layout; logo and branding on the shell only.  
- Desktop layout avoids page scroll where possible.

## Health checks

```bash
curl http://localhost:8000/api/health   # compress_assets
curl http://localhost:8100/api/health   # image_to_component
curl http://localhost:8200/api/health   # frontend-core-service
```

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| Docker permission denied | Add your user to the `docker` group, or use `sudo` for compose commands. |
| `docker compose` vs `docker-compose` | Use whichever is installed; `run.sh` expects `docker-compose`. |
| Compress fails / ffmpeg error | Install ffmpeg and restart the compress service. |
| Core tabs blank | Ensure services on ports **8000** and **8100** are up; check browser console and CORS (APIs allow all origins in dev). |
| Port already in use | Stop other processes or change ports in compose / `start.sh` / Vite config. |
| Image to component: non-SVG file | Only SVG is supported for path-based component generation. |

## System requirements

### All modes

- **Git** — clone the repository  
- **Bash** — for `start.sh` and `run.sh` (Linux/macOS; WSL on Windows)

### Docker workflow (recommended)

- **Docker** — Engine 20.10+ recommended  
- **Docker Compose** — v2 (`docker compose`) or v1 (`docker-compose`)  
- Enough disk space for three images and build cache  

### Local development (per service)

| Requirement | compress_assets | image_to_component | frontend-core-service |
|-------------|-----------------|--------------------|------------------------|
| **Node.js** (includes npm) | 18+ | 18+ | 18+ |
| **Python** | 3.10+ | 3.10+ | 3.10+ |
| **ffmpeg** | **Required** | — | — |

Install examples:

- **Node.js:** [https://nodejs.org](https://nodejs.org) (LTS)  
- **Python:** `python3`, `python3-venv`, `pip`  
- **ffmpeg:**  
  - Debian/Ubuntu: `sudo apt install ffmpeg`  
  - macOS: `brew install ffmpeg`  
  - Windows: install from [ffmpeg.org](https://ffmpeg.org) and ensure it is on `PATH`

Python dependencies are installed automatically by each `start.sh` into a local `.venv`. Frontend dependencies are installed via `npm install` in each `app` folder.

---

Developed by the IT team at **Dade Negar Eghtesad**.
