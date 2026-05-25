# Incident Runbook

## 1) MySQL unavailable
- Symptom: API returns DB connection errors.
- Immediate action:
  - Check DB container/process health.
  - Run connectivity test from API host.
- Recovery:
  - Restart DB service.
  - Run `alembic upgrade head` if schema drift exists.
- Post incident:
  - Check pool settings and connection saturation.

## 2) Redis unavailable
- Symptom: degraded auth refresh revocation/idempotency behavior.
- Immediate action:
  - Check Redis health and latency.
  - Validate network and credentials.
- Recovery:
  - Restart Redis.
  - Monitor replay protection after restart.
- Post incident:
  - Add Redis HA/sentinel for production.

## 3) RabbitMQ backlog
- Symptom: delayed background jobs.
- Immediate action:
  - Check queue depth in RabbitMQ UI.
  - Scale worker replicas.
- Recovery:
  - Purge poison messages to DLQ.
  - Reprocess dead-letter queue safely.
- Post incident:
  - Tune prefetch/retry/backoff policy.

## 4) Token abuse or brute-force attempts
- Symptom: repeated failed login attempts from same source.
- Immediate action:
  - Inspect auth lockout keys and access logs.
  - Block abusive IP at gateway/WAF.
- Recovery:
  - Rotate compromised credentials and secrets.
- Post incident:
  - Add anomaly alerts on failed-login thresholds.
