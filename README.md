# Find The Coffee ☕

Discover specialty coffee around you by searching across cafes, roasters, and specific beans.

## 🏗️ Architecture & Performance

This project implements a high-performance **Full-Text Search (FTS)** system using PostgreSQL:
- **Materialized View:** Pre-calculates expensive JOINs across the entire domain model.
- **GIN Indexing:** Provides sub-millisecond search results for complex queries.
- **Pydantic Validation:** Ensures type safety and data integrity at the API layer.
- **Dockerized Environment:** Fully orchestrated using Docker Compose (App + Database + Migrations).

## 🗺️ Domain Model

The relationship follows a "Source-to-Table" logic:

1.  **Roasters:** The source of the coffee. Each roaster can produce multiple beans.
2.  **Coffee Beans:** The specific product. Each bean is linked to exactly one Roaster.
3.  **Cafes:** The destination. A cafe can stock multiple beans from different roasters.
4.  **Cafe Inventory:** The join table that tracks which beans are currently available at which cafe.

### Relationship Diagram:
`Roaster` (1) --- (N) `Coffee Bean` (N) --- (N) `Cafe` (via Cafe Inventory)

## 🚀 Getting Started

### Prerequisites:
- Docker & Docker Compose

### Run the project:
```bash
docker compose up -d
```
The application will be available at:
- **Frontend:** http://localhost:8080
- **Backend API:** http://localhost:5000/api
- **Database:** localhost:5432

## 🌿 Branching & Contribution

This project follows a **GitHub Flow + Linear History** strategy, mimicking a **Gerrit-like** atomic review process:

- **Main Branch:** The source of truth. Always deployable.
- **Feature Branches:** Short-lived branches for specific tasks (e.g., `feat/add-roaster`, `fix/api-validation`).
- **Atomic Commits:** We prefer **One Pull Request = One Commit**. Use `git commit --amend` to update your work rather than adding new commits.
- **Linear History:** No "merge bubbles." All PRs are **Squashed and Merged** or **Rebased** onto `main`.

Refer to [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed workflow instructions.

## 🧪 Search API Examples

The global search (`/api/cafes?q=...`) uses the FTS index to search across:
- Cafe Name & Location
- Roaster Name
- Bean Name & Origin

Ranking (relevance) is calculated automatically based on where the match was found (Cafe Name > Roaster > Bean).
