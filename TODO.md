# Code Review: Major Improvement Areas

## 1. Incomplete Supabase Migration (Architectural / Technical Debt)

**Problem:** The backend (`app.py`) mixes an in-memory `db` dictionary with the Supabase client. Several critical functions (`find_best_matches`, `create_notification`, `check_upcoming_events`, `get_notifications`, `mark_notifications_read`, `get_volunteer_matches`) reference `db['users']`, `db['events']`, and `db['notifications']` which is never defined, causing runtime crashes.

**Impact:** Any route that touches volunteer matching, notifications, or upcoming event checks will fail with a `NameError`.

**Suggested Fix:**
- Migrate all `db[...]` references to Supabase queries.
- `find_best_matches()`: Query `supabase.table('users').select('*').execute()` instead of iterating `db['users']`.
- `create_notification()`: Insert into `supabase.table('notifications')` instead of appending to `db['notifications']`.
- `get_notifications()` and `mark_notifications_read()`: Query/update `supabase.table('notifications')` by username.
- `get_volunteer_matches()`: Query events from Supabase instead of `db['events']`.
- Remove the undefined `db` dictionary entirely.

---

## 2. Security Vulnerabilities (Security)

**Problem:** Multiple security issues exist across the stack:

| Issue | Location | Severity |
|-------|----------|----------|
| Hardcoded test credentials (`testuser@example.com` / `password123`) | `frontend/src/components/Login/Login.js:7-8,14` | Critical |
| Unrestricted CORS (`CORS(app)` allows all origins) | `backend/app.py:15` | High |
| No authentication middleware (all routes are public) | `backend/app.py` (all routes) | High |
| Debug mode enabled in production (`debug=True`) | `backend/app.py:338` | Medium |
| Raw exception messages returned to clients (`str(e)`) | `backend/app.py:188,202,232` | Medium |
| No rate limiting on auth endpoints | `backend/app.py:160,190` | Medium |

**Suggested Fix:**
- Replace hardcoded login with actual API calls to `/login`.
- Restrict CORS: `CORS(app, origins=["http://localhost:3000"])`.
- Add JWT-based authentication middleware to protect routes.
- Disable debug mode or use environment variable: `app.run(debug=os.getenv('FLASK_DEBUG', False))`.
- Return generic error messages to clients; log details server-side.
- Add Flask-Limiter for rate limiting on `/register` and `/login`.

---

## 3. Poor Code Quality & Maintainability (Technical Debt)

**Problem:** Several maintainability issues reduce code quality:

- **142 lines of commented-out legacy code** in `Event.jsx` (lines 11-142) that duplicates the active code below it.
- **No logging system** -- `print()` statements used for debugging in `app.py` and `supabaseClient.py`.
- **Duplicate Supabase client initialization** in `app.py`, `supabaseClient.py`, and `reporting.py` (3 separate clients).
- **Inconsistent response formatting** -- some routes use `create_response()`, others use raw `jsonify()` (`app.py:303-306,316-317,329`).
- **Magic numbers** -- match threshold `50` and `max_matches=5` hardcoded without named constants (`app.py:106,89`).
- **Validation bug** -- `EventSchema` requires `eventName` min 100 chars (should be ~5) (`Event.jsx:147`).
- **Unused imports and dead code** -- toast test buttons in `App.js` (lines 20-28, 36-41).
- **Deprecated `/src/` directory** at project root duplicates `/frontend/src/` components.

**Suggested Fix:**
- Remove all commented-out code from `Event.jsx`.
- Replace `print()` with Python `logging` module.
- Create a single shared Supabase client module and import it everywhere.
- Standardize all routes to use `create_response()`.
- Extract magic numbers into named constants (`MATCH_THRESHOLD = 50`, `MAX_MATCHES = 5`).
- Fix `EventSchema` validation (`min(5)` instead of `min(100)`).
- Remove toast test buttons from `App.js`.
- Delete the deprecated `/src/` directory.
