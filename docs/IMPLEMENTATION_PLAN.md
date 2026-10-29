# SENTINEL X Implementation Plan

## Stage A - Environment (completed)
- Python 3.12 available at E:\Naksh\python\python.exe with pip.
- Flutter 3.47.4 (stable) with Android SDK 36.1.0 and Chrome.
- PostgreSQL 18.6 running locally; created sentinel user/db.
- Visual Studio not installed -> Windows desktop builds unavailable.
- WSL kernel missing -> Linux desktop builds unavailable.
- Android Gradle build crashes in this environment (daemon disappears). Web build succeeds.

## Stage B - Foundations (completed)
- Monorepo scaffold created.
- FastAPI backend with SQLAlchemy models, routers, pytest suite.
- Flutter app with Material 3 dark theme, GoRouter, Riverpod, screens.
- Health checks and integration tests.

## Stage C - Functional slices
1. Case management: implemented (API + UI basic).
2. File Forensics Lab: hashing, signature detection, metadata; API + UI picker.
3. Log Investigation: CSV/JSON/text parsing, brute-force detection; API + tests.
4. Evidence Correlation & Timeline: timeline builder + API.
5. File Integrity Monitor: baseline + rescan + diff; API + tests.
6. Reports & audit trail: HTML report generation + audit events.
7. Sync: enqueue/complete/status; idempotency tests.
8. Ollama Cloud AI: client, context builder, citation validation, consent gating; mocked tests.

## Stage D - Cross-platform
- Web build: verified (flutter build web).
- Android build: not verified (Gradle daemon crash) - documented limitation.
- Windows/Linux: tooling unavailable - documented limitation.

## Stage E - Hardening
- ruff + pytest passing (30 backend tests, 3 agent tests, 1 Flutter test).
- Secret handling: API key only server-side; .env ignored.

## Known limitations
- Ollama model identifier must be supplied by user; no default invented.
- PDF generation depends on reportlab (available) but not wired to a dedicated endpoint beyond HTML; can be added.
- Local agent token optional; bind to loopback in production.
- Android build not validated in this environment.