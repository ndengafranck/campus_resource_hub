# Manual acceptance tests — FastAPI edition

1. Start DB, API and frontend. GET /api/health returns status ok; /docs opens.
2. Sign up with 10+ character password and mixed-case email; get 201 and JWT.
3. Repeat same email => HTTP 409 EMAIL_EXISTS.
4. Login wrong password => HTTP 401 BAD_CREDENTIALS.
5. Publish a valid resource; verify it appears for unauthenticated visitors.
6. Reject missing/invalid/unsupported resource URL => HTTP 422.
7. Sign up a second user. Second user's PUT/DELETE on first user's ID => 404; check row unchanged.
8. Call /api/external/books?title=algorithms; inspect normalized author and year.
9. Call /api/external/papers?query=machine%20learning; inspect DOI and year.
10. Simulate external outage by disabling network. Both external routes must fail gracefully, not crash app.
11. Stop the DB: health should fail; restart DB and verify automatic reconnect.
12. Logout in React; the create panel disappears; the public list still works.
