# Volunteer Management App - Code Review TODO

## Overview
This document summarizes findings from a senior-level code review of the entire codebase,
identifying 3 major areas for improvement across architecture, security, and technical debt.

---

## 1. Security Vulnerabilities (CRITICAL)

### Findings
- **Hardcoded credentials** in `frontend/src/components/Login/Login.js` (lines 7-8, 14):
  test email/password pre-filled and used for authentication bypass.
- **Duplicate Login file** (`Login.jsx`) contains the same hardcoded credentials.
- **Dummy registration data** pre-filled in `Registration.js` (lines 20-24).
- **Flask debug mode enabled** in `backend/app.py` (line 338): exposes stack traces to users.
- **Weak password policy**: only 6-character minimum, no complexity requirements.
- **No CSRF protection** on Flask API endpoints.
- **No rate limiting** on login endpoint, enabling brute-force attacks.
- **Hardcoded Supabase API keys** in test files (`test_volunteerMatching.py`, `test_volunteerHistory.py`).
- **No authentication context** in frontend: no JWT tokens, no session management.

### Suggested Improvements
- Remove all hardcoded credentials; use empty initial form values.
- Disable Flask debug mode; use environment variable to control it.
- Enforce password complexity (min 8 chars, uppercase, lowercase, number, special char).
- Add CSRF protection via `flask-wtf` or token-based validation.
- Add rate limiting with `flask-limiter`.
- Move all API keys to environment variables; never commit them.
- Implement JWT-based authentication with proper session management.

---

## 2. Architectural Issues (HIGH)

### Findings
- **Undefined `db` variable** in `backend/app.py` (lines 95, 122, 139, 259, 276, 286, 289):
  `find_best_matches()`, `create_notification()`, `check_upcoming_events()`, `get_notifications()`,
  and `mark_notifications_read()` all reference an in-memory `db` dict that doesn't exist.
  These functions will crash at runtime with `NameError`.
- **Missing `timedelta` import** in `app.py` (line 143): `check_upcoming_events()` will fail.
- **Frontend-backend disconnect**: Login, Registration, Profile, EventForm, and VolunteerMatch
  components have no backend API integration. Only VolunteerHistory makes actual API calls.
- **Hardcoded backend URL** (`http://localhost:5000`) in `volunteerHistory.js` - won't work
  in production.
- **Duplicate Supabase initialization**: `app.py`, `supabaseClient.py`, and `reporting.py` each
  create their own Supabase client independently.
- **Inconsistent database access**: some functions use Supabase SDK, others try to use
  undefined in-memory `db` dict.
- **No global state management** in frontend: no Context, Redux, or Zustand for auth state.

### Suggested Improvements
- Replace all `db` references in `app.py` with proper Supabase queries.
- Add missing `timedelta` import.
- Create a shared Supabase client module used by all backend files.
- Create an API configuration module in frontend (use env vars for base URL).
- Integrate all frontend forms with backend API endpoints.
- Add React Context for authentication state management.
- Add protected routes that require authentication.

---

## 3. Technical Debt & Code Quality (MEDIUM-HIGH)

### Findings
- **130+ lines of commented-out code** in `frontend/src/components/EventForm/Event.jsx`
  (lines 11-142): old implementation left as comments instead of using version control.
- **Duplicate Login files**: both `Login.js` and `Login.jsx` exist with nearly identical code.
- **Validation bug** in `Event.jsx` (line 147): event name requires 100 characters minimum
  (should likely be ~5).
- **Label mismatch** in `Event.jsx` (line 157): value says "20 miles" but label says "50 miles".
- **Form-Formik conflict** in `Event.jsx` (line 214): `handleSubmit` on both `<Form>` and
  Formik's `onSubmit`, causing double submission handling.
- **Select not integrated with Formik** in `Event.jsx`: React-Select value not synced with
  Formik state.
- **DatePicker not integrated with Formik** in `Event.jsx`: date value not submitted.
- **Print statements used for logging** in `backend/supabaseClient.py` and `app.py` instead of
  Python's `logging` module.
- **Inconsistent response format**: some routes use `create_response()`, others use raw `jsonify()`.
- **No loading states** in frontend components during async operations.
- **No error boundaries** in React application.
- **Temp test buttons** left in `App.js` (lines 20-41).
- **Test files largely broken**: many tests commented out, reference undefined `db`, or have
  wrong assertions.

### Suggested Improvements
- Delete all commented-out code; rely on git history.
- Remove duplicate `Login.jsx` file.
- Fix validation schema values (eventName min length, skill label mismatch).
- Properly integrate React-Select and DatePicker with Formik using `setFieldValue`.
- Replace print statements with Python `logging` module.
- Standardize all API responses to use `create_response()` helper.
- Add loading states and error boundaries to React components.
- Remove temp test buttons from `App.js`.
- Rewrite broken tests to use Supabase queries instead of `db` dict.

---

## Priority Order
1. Fix security vulnerabilities (hardcoded creds, debug mode, API keys)
2. Fix runtime crashes (undefined `db`, missing imports)
3. Clean up technical debt (commented code, duplicates, broken tests)
4. Add proper frontend-backend integration
5. Add authentication context and protected routes
6. Add comprehensive test coverage
