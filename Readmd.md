# Araf E-commerce (FastAPI Backend)

## 1) Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
```

## 2) Configure environment
Create `.env` in project root:

```env
APP_NAME=Araf E-commerce API
APP_VERSION=0.1.0
API_PREFIX=/api/v1

DATABASE_URL=mysql+pymysql://root:root@localhost:3306/araf_ecommerce
SECRET_KEY=change-this-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
APP_ENV=development
LOG_LEVEL=INFO
REQUEST_TIMEOUT_SECONDS=30
MAX_REQUEST_SIZE_BYTES=1048576
LOGIN_MAX_ATTEMPTS=5
LOGIN_LOCK_MINUTES=15
OTEL_ENABLED=true
OTEL_SERVICE_NAME=araf-ecommerce-api
OTEL_EXPORTER_OTLP_ENDPOINT=
OTEL_EXPORTER_OTLP_INSECURE=true

RATE_LIMIT_PER_MINUTE=60
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672//

DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123
```

## 3) Start infrastructure (recommended via Docker)
```bash
docker compose up -d
```

Services included:
- MySQL
- Redis
- RabbitMQ (management UI on `http://127.0.0.1:15672`)
- OpenTelemetry Collector
- Jaeger UI (`http://127.0.0.1:16686`)
- Celery worker
- Flower dashboard (`http://127.0.0.1:5555`)

## 4) Run API server
```bash
uvicorn main:app --reload
```

Open Swagger: `http://127.0.0.1:8000/docs`

## 5) Auth flow
1. Call `POST /api/v1/auth/token` with form-data:
	- `username=admin`
	- `password=admin123`
2. Copy `access_token`
3. Use `Authorization: Bearer <token>` for category APIs
4. Refresh token when access token expires:
   - `POST /api/v1/auth/refresh`
   - Body: `{ "refresh_token": "..." }`

## 6) Category CRUD APIs
- `GET /api/v1/categories?search=elec&page=1&size=10`
- `POST /api/v1/categories`
- `PUT /api/v1/categories/{category_id}`
- `DELETE /api/v1/categories/{category_id}`

All category routes are guarded with OAuth2 JWT auth.

## 6.1) Category image upload (background processing)
Upload endpoint:
- `POST /api/v1/categories/{category_id}/image`
- Content-Type: `multipart/form-data`
- Field name: `image`

Behavior:
1. API stores original image under `media/uploads/categories`.
2. API creates image job record (`queued`).
3. Celery task is enqueued via RabbitMQ.
4. Celery worker processes image in background and saves a processed file copy under `media/processed/categories`.
5. Job status updates to `completed` or `failed`.

Supported file formats:
- `.jpg`, `.jpeg`, `.png`, `.webp`

Processed files are accessible via:
- `/media/...`

## 6.2) Image job monitoring and retry
Admin endpoints (admin token required):
- `GET /api/v1/admin/image-jobs`
- `GET /api/v1/admin/image-jobs?status=failed`
- `POST /api/v1/admin/image-jobs/{job_id}/retry`
- `GET /api/v1/admin/image-jobs-dashboard`

Dashboard UI options:
- Flower task dashboard: `http://127.0.0.1:5555`
- In-app admin dashboard with failed-job retry buttons: `GET /api/v1/admin/image-jobs-dashboard`
	- Paste admin bearer token in the page
	- Load failed jobs
	- Click Retry for any failed job

## 7) Migrations with Alembic
Create/upgrade schema with Alembic:

```bash
alembic upgrade head
```

If your DB was created before Alembic tracking (for example via `Base.metadata.create_all()`), the first upgrade can fail with `table already exists`. Reconcile by stamping the baseline, then upgrading:

```bash
alembic stamp 20260526_0001
alembic upgrade head
```

If the objects from `20260526_0002` already exist too, stamp directly to head:

```bash
alembic stamp head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "your_message"
```

Initial migration file:
- `alembic/versions/20260526_0001_init_schema.py`

Legacy SQL file is still available at:
- `migrations/0001_create_users_categories.sql`

## 8) Run tests
```bash
pytest -q
```

## 9) Health endpoints
- `GET /health` returns basic API status.
- `GET /health/dependencies` performs live Redis and RabbitMQ checks.
	- Returns `200` when both are ready.
	- Returns `503` when one or more dependencies are unavailable.

## 10) Metrics endpoint
- `GET /metrics` exposes Prometheus metrics.

## 10.1) Tracing
- OpenTelemetry tracing is enabled with OTLP exporter support.
- Set `OTEL_EXPORTER_OTLP_ENDPOINT` to your collector URL to export traces.
- Response headers include:
	- `X-Request-ID`
	- `X-Trace-ID`
- Logs include both `request_id` and `trace_id` for correlation.

### Local tracing with Docker Compose
- `docker compose up -d` starts API + MySQL + Redis + RabbitMQ + OTel Collector + Jaeger.
- API traces are preconfigured to export to collector via:
  - `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces`
- Open Jaeger UI:
  - `http://127.0.0.1:16686`

## 11) Production controls implemented
- Structured JSON logging with request and user context.
- Request ID propagation via `X-Request-ID`.
- Standardized global error response shape.
- Request timeout and payload size guardrails.
- Idempotency key support for write endpoints (`Idempotency-Key`).
- Login brute-force lockout by username and client IP.
- Refresh token rotation with revoke tracking (Redis-backed with safe fallback).
- Endpoint-specific rate limits for auth APIs.

## 12) CI and security automation
- CI workflow: `.github/workflows/ci.yml`
- Security workflow: `.github/workflows/security.yml`

## 13) Operational docs
- Production standards: `docs/production-standards.md`
- Incident runbook: `docs/runbooks/incidents.md`