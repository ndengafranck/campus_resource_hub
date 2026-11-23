# Campus Resource Hub — FastAPI Guided Implementation (IUC BTECH 3 CSE)

This is the **FastAPI replacement of the Express backend** for the Campus Resource Hub capstone. It preserves the React UI and PostgreSQL schema from the original Full-Stack course while adding a second external integration (Crossref scholarly metadata).

## Stack
- Frontend: React + Vite (port 5173)
- Backend: Python + FastAPI + SQLAlchemy Core + psycopg v3 (port 8000)
- DB: PostgreSQL 17 in Docker Compose (port 5432 on localhost only)
- External APIs: Open Library Search + Crossref Works

## Linux / Ubuntu setup
1. Ensure Python 3.11+ (recommended 3.12), Node.js 22+, npm and Docker Compose are installed.
2. From the repository root, `docker compose up -d db`.
3. `cd backend && python3 -m venv .venv && source .venv/bin/activate`.
4. `python -m pip install -r requirements-dev.txt`.
5. `cp .env.example .env` and replace JWT_SECRET with a random value generated using `openssl rand -hex 32`. Do **not** publish this file.
6. `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
7. API docs: http://127.0.0.1:8000/docs ; health: http://127.0.0.1:8000/api/health
8. In a second terminal, `cd frontend && cp .env.example .env && npm install && npm run dev`.
9. Open http://localhost:5173.

Use `python -m pytest -q` in backend to run offline unit tests. They mock external providers and **do not require PostgreSQL**. DB-backed integration tests are a student extension.

## curl smoke tests
```bash
curl -i http://127.0.0.1:8000/api/health
curl -G --data-urlencode 'title=computer networks' http://127.0.0.1:8000/api/external/books
curl -G --data-urlencode 'query=machine learning' http://127.0.0.1:8000/api/external/papers
curl -X POST http://127.0.0.1:8000/api/auth/register -H 'Content-Type: application/json' \
  -d '{"fullName":"Ada Example","email":"ada@example.edu","password":"strong-demo-password"}'
```
Copy `data.accessToken` from registration into `$TOKEN` and run:
```bash
curl -X POST http://127.0.0.1:8000/api/resources -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"React handbook","description":"Official React documentation","url":"https://react.dev/learn","category":"lecture"}'
```

## Teaching scope and limitations
- Development credentials and direct browser-held JWT are for local labs only; no HTTPS reverse proxy or production session security is supplied.
- No production account recovery, mail verification, token rotation/revocation, login rate-limiting, DB migration pipeline, deployment automation or instrumentation.
- External provider tests are mocked offline; external APIs may impose limits and may be unavailable.
- The educational DB schema is created only on first volume initialization (`db/schema.sql`). `docker compose down -v` deletes the demo database permanently.
- Never place real student personal data in experiments, screenshots or external API calls.

See `docs/api-contract.md` and `docs/manual-test-cases.md`.
