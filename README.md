# Vision Curator

Vision Curator is a local web application for turning videos into curated computer-vision frame datasets. Phase 2 adds timeline navigation, server-side batch actions, configurable shortcuts, persistent review queues, statistics, unified job recovery, multi-step undo/redo, integrity repair, and a polished responsive interface to the complete Phase 1 curation workflow.

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- A browser supported by Chromium

## Clean setup

Create and activate the repository-local Python environment **before installing any Python package**:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e './backend[dev]'
npm ci --prefix frontend
cp .env.example .env
```

All Python commands below either assume `.venv` is active or call its executables explicitly. Application data is local: the default SQLite database is `backend/vision_curator.db`, and managed media, thumbnails, and exports are under `storage/`.

## Database migrations

Apply all migrations before the first run and after pulling schema changes:

```bash
cd backend
../.venv/bin/alembic upgrade head
../.venv/bin/alembic current
cd ..
```

The expected Phase 2 candidate head is `20260804_0010`. Migrations retain existing SQLite data. Back up valuable databases before downgrading or changing migration history.

## Run locally

Backend, from the repository root:

```bash
cd backend
../.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend, in another terminal:

```bash
cd frontend
npm run dev
```

Open <http://localhost:3000>. The API health check is <http://localhost:8000/api/v1/health>, and interactive API documentation is at <http://localhost:8000/docs>.

## Curation workflow

1. Create a project from **Projects**. Each project gets an isolated directory under `storage/projects`.
2. Open it and import one or more MP4, AVI, MOV, MKV, or WebM files. Folder selection skips unsupported files and reports corrupt media without stopping the rest of the batch.
3. Start extraction for a video. Choose every N frames, frames per second, or every N seconds; select JPEG/PNG and optional resize limits. Jobs run outside the request thread and can be cancelled.
4. Open the gallery. Results are paginated at no more than 200 frames and rows are virtualized, so the browser only renders nearby thumbnails.
5. Select with click, Ctrl/Cmd-click, or Shift-click. Create labels and apply them to one or many frames. Filter by video, labels, review state, favorite/rejected/unlabeled state, timestamp range, filename, or frame number.
6. Double-click a thumbnail for the full-resolution viewer. Use the controls for fit/original size and zoom; zoomed content can be panned.
7. Export selected, favorite, reviewed, or labeled frames, or create only a manifest. Choose duplicate handling and whether multi-label images are copied into every label folder.

Label and review changes are written immediately to SQLite. The last project, filters, page/position, thumbnail size, and opened frame are restored when the application is reopened.

## Phase 2 tools

- Filter to one video to open its timeline. Drag or use Home/End/arrow keys, click representative extraction markers, or jump to the closest extracted frame by exact timestamp or source frame number.
- Use **Select visible**, **Select all filtered**, **Invert visible**, and **Clear selection**. Large bulk actions show their affected count and require confirmation; all-filtered operations resolve IDs on the server.
- Create stable review queues from unreviewed, video, label, rejected, favorite, random, or custom-filtered frames. Queue position and progress survive restarts.
- Open the statistics dashboard for aggregated label, status, video, job, and review-progress charts. Filter it by video and date.
- Inspect unified extraction, export, and thumbnail job history. Interrupted work is marked safely after restart and can be retried; concurrency defaults to two active jobs.
- Use persisted action history to undo and redo label and review operations, including bulk changes.
- Run a project integrity check to report missing/unsafe videos, frames, and thumbnails and safely regenerate repairable thumbnails.
- Use **Settings** to customize shortcuts, restore defaults, and select a light or dark theme. First-run onboarding, recent projects, notifications, drag-and-drop import, and responsive layouts are included.

## Keyboard shortcuts

In the viewer:

| Key | Action |
| --- | --- |
| Left arrow or `A` | Previous frame |
| Right arrow or `D` | Next frame |
| `F` | Toggle favorite |
| `R` | Toggle rejected |
| Space | Toggle reviewed |
| Escape | Close viewer |

Each label can also have a unique shortcut. Label shortcuts act on the current selection or open frame and are ignored while typing in an input, textarea, or select. Viewer/gallery shortcuts can be changed under **Settings**; conflicts are rejected and preferences persist in local browser storage.

## Configuration

Copy `.env.example` to `.env` and adjust these values if needed:

- `VISION_CURATOR_DATABASE_URL`: SQLAlchemy SQLite URL.
- `VISION_CURATOR_STORAGE_ROOT`: storage location; relative values resolve from `backend/`.
- `VISION_CURATOR_CORS_ORIGINS`: JSON list of allowed frontend origins.
- `VISION_CURATOR_CONCURRENT_JOB_LIMIT`: maximum active extraction, export, and maintenance jobs; default `2`.
- `VITE_API_URL`: frontend API base URL.

Do not expose this local application beyond localhost without adding authentication and reviewing its CORS and filesystem policy.

## Verification

```bash
source .venv/bin/activate
ruff check backend/app backend/tests
mypy backend/app
pytest -q backend/tests

cd frontend
npm test
npm run lint
npm run format:check
npm run build
npm run test:e2e
npm audit
```

The Playwright check starts both local servers and performs the complete workflow using a generated test video, then verifies timeline/queue navigation and responsive persisted settings. If Chromium is absent, install the test browser once with `npx playwright install chromium`. The 100,000-frame backend test is part of `pytest`; it asserts bounded 100-record responses, a sub-second filtered query, and use of the intended SQLite index. See the [Phase 2 verification report](docs/phase-2-verification.md).

## Architecture and data safety

The React/Vite TypeScript client uses TanStack Query for cancellable API requests, Zustand for UI state, and TanStack Virtual for gallery rows. FastAPI routes delegate persistence, aggregation, and media work to typed service classes backed by SQLAlchemy, Alembic, SQLite, OpenCV, and Pillow. Extraction, export, and thumbnail workers expose unified progress, cancellation, history, retry, concurrency limits, and restart recovery through REST polling.

Original videos are never modified. Imports are copied into managed project storage, labeling only updates SQLite relations, thumbnails are cached separately, and exports copy source frames. Project deletion requires browser confirmation and removes the database record without recursively deleting the project directory. Export destinations are constrained beneath the configured export root.

## Troubleshooting and limitations

- API unavailable: confirm the backend is on port 8000 and `VITE_API_URL` matches it.
- Migration targets the wrong file: inspect `VISION_CURATOR_DATABASE_URL` and run `alembic current` from `backend/`.
- Storage errors: set `VISION_CURATOR_STORAGE_ROOT` to a writable directory.
- Corrupt video: verify OpenCV can decode the codec; the import result includes a readable per-file error.
- Missing thumbnail: request it again from the gallery; a valid thumbnail is regenerated from the full frame.
- This is a single-user local product. Jobs run in the backend process rather than a distributed queue; terminating that process marks active jobs interrupted on restart so they can be retried.
- Gallery navigation is page-bounded (up to 200 records at once); move between pages to traverse larger result sets.
- Review queues store stable frame membership in SQLite. Very large queue creation therefore increases database size, although queue responses do not transfer all member IDs to the browser.
- The `phase-2-complete` tag remains gated on a real teammate completing a workflow and recording feedback in [the feedback template](docs/phase-2-feedback.md).
