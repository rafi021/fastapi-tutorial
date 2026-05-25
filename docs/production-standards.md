# Production Standards

## Security
- Enforce HTTPS at ingress and redirect HTTP to HTTPS.
- Store secrets in a secret manager, not repository files.
- Rotate JWT signing keys and DB credentials periodically.
- Keep login lockout, endpoint-level rate limits, and request size limits enabled.

## API Reliability
- Keep `/health` for liveness and `/health/dependencies` for readiness.
- Use idempotency keys on write APIs from clients.
- Keep global exception shape stable for all responses.

## Data and Migrations
- Use Alembic for all schema changes.
- Block deploy if migration step fails.
- Review indexes for query-heavy endpoints before release.

## Observability
- Use structured JSON logging with request and user context.
- Scrape `/metrics` with Prometheus.
- Define alerts for 5xx rate, p95 latency, queue backlog, and DB connectivity.

## CI/CD Gates
- Run tests and migration checks on each PR.
- Run dependency and container vulnerability scans.
- Publish immutable image tags and promote via environments.

## Operations
- Maintain runbooks in `docs/runbooks`.
- Define SLO targets and incident response ownership.
- Verify backup restore procedure regularly.
