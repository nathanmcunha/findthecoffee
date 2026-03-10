# Security and Privacy Audit Report - March 10, 2026

## Executive Summary
This report details the findings of a security and privacy audit conducted on the Coffee Finder project. The audit identified one High-severity vulnerability (XSS) and several Medium to Low-severity risks related to information disclosure and credential management.

---

## Findings

### 1. Stored Cross-Site Scripting (XSS)
*   **Vulnerability Type:** Security
*   **Severity:** High
*   **Source Location:** `frontend/script.js` (Lines 92, 110)
*   **Description:** User-supplied data (cafe names, locations, and bean details) fetched from the backend is directly rendered into the HTML DOM using template strings and jQuery's `.append()` method without any sanitization or escaping.
*   **Impact:** An attacker could inject malicious scripts that execute in the context of other users' browsers.
*   **Recommendation:** Use safe DOM manipulation methods like jQuery's `.text()` or a secure templating library. Sanitize Leaflet popup content.

### 2. Verbose Error Messages (Information Disclosure)
*   **Vulnerability Type:** Security
*   **Severity:** Medium
*   **Source Location:** `backend/app.py` (Lines 37, 55, 74, 88, 101, 117, 139)
*   **Description:** Internal exceptions are converted to strings and returned directly to the client via `jsonify({"error": str(e)})`.
*   **Impact:** Disclosure of sensitive backend details (DB schema, file paths) to potential attackers.
*   **Recommendation:** Use generic error messages for production and log detailed errors on the server.

### 3. Hardcoded Sensitive Information (Credentials)
*   **Vulnerability Type:** Security
*   **Severity:** Medium (Production Risk)
*   **Source Location:** `docker-compose.yml` (Line 7), `backend/seed_data.py` (Line 74)
*   **Description:** Database credentials are hardcoded in configuration and seed scripts.
*   **Impact:** Potential exposure of credentials if files are committed to version control.
*   **Recommendation:** Use environment variables or a secure secrets management system.

### 4. Overly Permissive CORS Policy
*   **Vulnerability Type:** Security
*   **Severity:** Low
*   **Source Location:** `backend/app.py` (Line 12)
*   **Description:** Flask-CORS is initialized with default settings, allowing all origins (`*`).
*   **Impact:** Potential for unauthorized third-party websites to interact with the API.
*   **Recommendation:** Restrict CORS to specific, trusted frontend domains.

---
*End of Report*
