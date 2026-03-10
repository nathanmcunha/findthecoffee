# Code Review Feedback - March 10, 2026 (POC Phase)

## Overview
This document captures architectural, logic, and security issues identified during the "Decoupled Architecture" refactor. These are prioritized for resolution after the initial POC validation.

---

## 1. Functional & Logic Gaps

### [CRITICAL] Undefined `bean_repo.search()`
*   **File:** `backend/app.py:85`
*   **Issue:** The `/api/beans` endpoint attempts to call a `search()` method on the repository that has not been implemented.
*   **Impact:** This route will crash with an `AttributeError` on every request.
*   **Suggested Fix:** Implement a dynamic SQL builder in `CoffeeBeanRepository` to handle optional `roast_level` and `origin` parameters.

### [MEDIUM] Hardcoded API Endpoint in Frontend
*   **File:** `frontend/script.js:1`
*   **Issue:** `API_BASE_URL` is hardcoded to `http://localhost:5001/api`.
*   **Impact:** The frontend will fail when deployed to any environment other than the local dev machine (e.g., Kubernetes, Staging).
*   **Suggested Fix:** Use a relative path or a runtime configuration inject.

---

## 2. Security & Stability

### [HIGH] DOM-based XSS in Result Rendering
*   **File:** `frontend/script.js:92` & `frontend/script.js:110`
*   **Issue:** Using `.append()` with raw template strings and `.bindPopup()` with raw HTML.
*   **Impact:** Malicious data in the database (e.g., a cafe name containing `<script>`) will execute in the user's browser.
*   **Suggested Fix:** Use jQuery's `.text()` for data injection or sanitize HTML using a library like DOMPurify.

### [MEDIUM] Information Disclosure in Error Handling
*   **File:** `backend/app.py` (Multiple locations)
*   **Issue:** `jsonify({"error": str(e)})` returns raw Python exception messages to the client.
*   **Impact:** Leakage of database structure, internal paths, and logic details.
*   **Suggested Fix:** Log the error server-side and return a generic "Internal Server Error" message to the client.

---
*Note: This is a POC-only baseline. Production deployment requires addressing all [CRITICAL] and [HIGH] items.*
