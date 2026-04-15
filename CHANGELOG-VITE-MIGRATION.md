# Frontend Vite Migration

## Summary

This migration replaces the Deno-based build system with Vite for both development and production builds. The goal was to simplify the frontend toolchain by removing Deno dependency and using modern tooling.

## Changes Made

### 1. Removed Deno Dependency
- Removed `deno` from `.mise.toml` tools section
- Deleted `frontend/scripts/build.ts`
- Cleaned up `deno.json` configuration

### 2. Added Vite
- Added `vite` and `@tailwindcss/vite` to `frontend/package.json`
- Created `frontend/vite.config.mts` with:
  - Tailwind CSS v4 plugin integration
  - Dev server on port 3000
  - API proxy to `http://localhost:5000`

### 3. Updated Frontend Scripts (`frontend/package.json`)
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "typecheck": "tsc --noEmit"
  }
}
```

### 4. Updated Entry Point
- Changed `frontend/index.html` script src from `dist/main.js` to `/src/main.ts` for Vite

### 5. Simplified Mise Tasks (`.mise.toml`)
| Task | Description |
|------|-------------|
| `mise ts` | Type-check with tsc |
| `mise js` | Vite production build |
| `mise js:watch` | Vite dev server with HMR |
| `mise up:frontend` | Alias for js:watch |
| `mise dev` | Backend (Docker) + frontend (Vite) |

### 6. Updated Dockerfiles
- `frontend/Dockerfile`: Uses `npm run build` instead of Deno commands
- `frontend/Dockerfile.runtime`: Same updates

### 7. Simplified Scripts
- Created `scripts/start-dev.sh` to orchestrate Docker + Vite
- Deleted old build scripts (build-dev.sh, build-prod.sh, download-tailwind.sh, watch.sh, serve-frontend.py)

### 8. Updated Gitignore
- Removed `frontend/style.css` and `frontend/tailwindcss`
- Added `frontend/node_modules/` and `frontend/dist/`
- Added `logs/` and `.pids/` for dev environment

## Before/After Comparison

### Before (Deno-based)
```bash
# Build
mise run js:build  # Deno bundle + Tailwind CLI

# Dev
mise run docker:dev & mise run up:frontend & mise run js:watch & wait
```

### After (Vite-based)
```bash
# Build
npm run build      # or: mise run js

# Dev
mise run dev       # Docker backend + Vite frontend
```

## Dependencies Added
- `vite@^5.4.0`
- `@tailwindcss/vite@^4.2.2`

## Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server (http://localhost:3000) |
| `npm run build` | Production build to `frontend/dist/` |
| `npm run typecheck` | TypeScript type check |
| `mise run js` | Alias for npm run build |
| `mise run js:watch` | Alias for npm run dev |
| `mise run dev` | Full stack (backend + frontend) |
| `mise run build:prod` | Type check + production build |

## Notes
- Vite handles hot module replacement automatically
- No need for custom file watchers
- API proxy configured for local development
- Tailwind v4 integrated via `@tailwindcss/vite` plugin