# Campus Resource Hub — API contract, FastAPI implementation

**Base URL:** `http://localhost:8000/api` · **OpenAPI/Swagger:** `http://localhost:8000/docs` · **JSON schema:** `/openapi.json`

All successes use `{ "data": ... }` (resource lists also use `{ "meta": ... }`).
All validation/auth/provider errors use `{ "error": { "code": "...", "message": "..." } }`.

| Method | Path | Authentication | Typical status |
|---|---|---|---|
| GET | /health | none | 200 (DB check) |
| POST | /auth/register | none | 201 |
| POST | /auth/login | none | 200 |
| GET | /auth/me | Bearer | 200 / 401 |
| GET | /resources?q=...&page=1 | none | 200 |
| GET | /resources/{id} | none | 200 / 404 |
| POST | /resources | Bearer | 201 |
| PUT | /resources/{id} | owner | 200 / 404 |
| DELETE | /resources/{id} | owner | 204 / 404 |
| GET | /external/books?title=... | none | 200 / 502 / 503 |
| GET | /external/papers?query=... | none | 200 / 502 / 503 |

POST /auth/register: `{"fullName":"Ada Example","email":"ada@example.edu","password":"strong-demo-password"}`

POST /resources: `{"title":"React docs","description":"Official tutorial","url":"https://react.dev/learn","category":"lecture"}`

Important: ID ownership is checked on the SQL UPDATE/DELETE. Another user's record returns 404; the record is never modified.

**Difference from default FastAPI:** validation errors are adapted to `{error: ...}` with status 422 to keep the existing React client compatible. Automatic generated docs still describe the Pydantic input models; the teaching project intentionally does not define full response models.
