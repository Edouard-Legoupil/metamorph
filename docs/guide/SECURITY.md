# Metamorph Security Practices and Audit

## 1. Perimeter Security: Ingestion, API, and Cache

- **/ingest API is protected** by API key or internal IP allow, never public.
- **Payload size enforced** (suggested default: 20MB), with 413 on larger requests.
- **Disk-backed cache has strict size+TTL;** oldest and least recent entries are pruned, and heavy/binary (>20MB) rejected.
- **All logs redact secrets (API keys, tokens, credentials)** and do not output raw files in error traces.
- **Only HTML/JSON/XML/PDF is accepted**; non-conforming content is quarantined or skipped.
- **Cloudflare credentials set by env only**; never hardcoded or in repo/Docker.

---

## 2. App Security: Auth, Trust, Curation, Audit

- **All modifying endpoints require authentication**—API key for agents/MCP, and session/JWT for all curator/approval endpoints.
- **CSRF protection enabled** for browser API endpoints.
- **Markdown and all HTML rendered is sanitized** before display to block XSS.
- **Audit logs** are immutable, chained and exported daily for review; all agentic/curation actions (approve, flag, escalate, deliver, etc) retain `actor`, `event_type`, `details`, `timestamp`.

---

## 3. Deployment Security

- **All secrets managed in deploy environment** (Kubernetes secrets, Docker secrets, Vault); never in git.
- **HTTPS enforced** at all API endpoints and documented in API.md.
- **Dependency pinning** and CI run `pip-audit`, `bandit`, and `npm audit` before deploy.
- **Operator monitoring for cache overflow, ingest failures, and CVEs.**
- **All environment separation (dev/stage/prod) strictly maintained.**

---

## 4. Incident Response & Practice

- **Rotate all API keys and MCP keys regularly;** remove any unused or stale keys.
- **Review audit logs** after any failed delivery, incident, or agentic escalation.
- **Quarantine suspect content and re-run with clean credentials.**

#### See also: [docs/OPS.md](OPS.md) and [docs/CLI.md](CLI.md) for operational procedures.

---

## 5. Continuous Security Review
- Operators are strongly encouraged to:
  - Re-run dependency audits and system scans weekly.
  - Retest all CSRF/XSS controls on curation and ingest endpoints.
  - Review agent and human activity logs with the audit tool (`mcp/audit.py` or SIEM export).
