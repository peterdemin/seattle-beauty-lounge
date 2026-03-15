# Seattle Beauty Lounge

This repository is a hybrid web application with a Python backend API and a React/Vite-based static frontend/content system.

The project is organized around two main execution paths:
- **API server**: FastAPI app that serves JSON endpoints and optional static files.
- **Static site + booking UI**: Built from markdown/reStructuredText content and React bundles into `/public`.

## Repository Layout

- `api/` — FastAPI backend
  - `main.py` app factory entrypoint
  - `app.py` creates app, wiring settings, DB, background tasks, endpoints
  - `config.py` environment-driven feature flags and integrations
  - `models.py`, `db.py`, `kv.py` data layer and tables
  - `endpoints/` request handlers
    - `appointments.py` customer APIs (`/appointments`, `/appointment/{id}`, `/availability`)
    - `backoffice.py` admin APIs (`/admin/appointment/{id}`, optional `/admin/build`)
  - `tasks/` background jobs (calendar, reminder emails, availability sync)
  - `slots.py` booking availability generation
  - `calendar_client.py`, `square_client.py`, `sms_client.py`, `smtp_client.py`, `google_auth.py` integrations
- `source/` — website source content and templates
  - `scripts/` React entry pages and components
    - `index.html` + `booking-bootstrap.jsx` (booking modal entry)
    - `appointment.html` + `ChangeAppointment.jsx` (public appointment view)
  - `templates/` Jinja HTML templates
  - `pages/` markdown snippets and policy text
  - `styles/` Tailwind input + shared tokens
  - `images/` source images and snippet/media files
- `frontend/` — build engine for static site generation
  - `cli.py` command interface
  - `builder.py` step-based build pipeline
  - `renderer.py`, `service_parser.py`, `javascript_embedder.py`, `image_publisher.py`, `tailwind.py`
- `lib/` — shared domain objects and content pickle helpers
  - `service.py` service/ snippet dataclasses and load/dump logic
  - `jd.py` naming helper for content indices
- `admin/` — lightweight admin React app
  - `admin.html`, `Appointment.jsx`
- `tests/` — API/frontend tests and Playwright E2E
- `tools/` — deploy/provision scripts
- `public/` — build output target served by the app in production mode

## Routing and Admin Mounting

This repo has two API base layers to understand:

- **API prefixing inside FastAPI**
  - Endpoints are mounted with `location_prefix` from `Settings`.
  - `LOCATION_PREFIX=/api` turns:
    - customer APIs into `/api/appointments`, `/api/availability`, `/api/appointment/{pubid}`
    - backoffice APIs into `/admin/api/appointment/{id}` and `/admin/api/build`
  - `location_prefix` is configured in [api/config.py](/Users/peterdemin/seattle-beauty-lounge/api/config.py) and loaded from `.env`.

- **Nginx fronting in deployment**
  - In production config, `api/etc/nginx/sites-available/default`, `a.seattle-beauty-lounge.com` handles `location /admin/` and proxies to `http://api/admin/`.
  - Main production host handles `location /api` for backend API calls.
  - `location /admin/` in production has explicit allowlist (`100.64.0.0/10`, loopback) plus `deny all`.
  - Staging config, `api/etc/nginx/sites-available/staging`, proxies both:
    - `/api/` -> `http://api/api/`
    - `/admin/` -> `http://api/admin/`
  - Staging applies VPN-only access at the whole server block level, so every request is constrained, not just admin routes.
  - Deployment applies Nginx updates via `api/deploy.sh` (which copies `api/etc/nginx/sites-available/default` to `/etc/nginx/sites-available/default` and reloads nginx).

## Core Runtime Flow

1. Frontend booking loads from built templates in `public/`.
2. User flow renders `BookingWizard` from `source/scripts/BookingWizard.jsx`.
3. `GET /api/availability` computes open ranges via `api.slots -> DayBreaker`.
4. `POST /api/appointments` validates and stores an appointment.
5. Background tasks dispatch:
   - confirmation/owner emails
   - calendar event creation (when enabled)
6. Appointment detail page fetches `/api/appointment/{pubid}`.

## Build Flow

1. `frontend` parses content from `source/` and `source/7-media`:
   - service definitions from `source/[123]-*/[0-9][0-9]-*.rst`
   - snippets/snippets/media from `7-media`
2. Vite build runs via `npm` for frontend/admin bundles.
3. Rendered HTML and assets are written to `/public`.
4. Images are published from source folders into `public/images`.

## Environment / Config

The app reads settings from environment variables via Pydantic in `api/config.py`.
Local developer settings in a repo-local `.env` (loaded by `api/config.py` and used for local runs).
Production/staging credentials live outside of repository.

### Deployment environment pattern

Deployment scripts:
- `tools/deploy_production.sh`
- `tools/deploy_staging.sh`
- `api/deploy.sh`

## Useful Commands

### Frontend + backend dev
- `make dev` — build frontend (`make fe`) and run FastAPI dev server (`api/main.py`)
- `npm run dev` — run Vite dev server directly

### Build modes
- `make fe` — development frontend build
- `make staging` — production-like frontend staging build
- `make prod` — production frontend build
- `make content` — sync content/generate source artifacts
- `make jstest` — run JS availability test helper

### Python tasks
- `make test` — pytest + coverage for api/frontend/lib
- `make lint` / `make lint-python` / `make lint-js`

## Notes

- The admin app is mounted by default under `/admin` when enabled in settings.
- Backoffice features are gated by `enable_admin` and optional admin build flag.
