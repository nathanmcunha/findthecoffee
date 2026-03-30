# Frontend Development Guidelines

## TypeScript Best Practices

### ✅ DO: Use TypeScript Sources

**All code must be written in `.ts` files under `frontend/src/`**

```typescript
// ✅ CORRECT: frontend/src/api.ts
export async function fetchCafes(filters: CafeFilters): Promise<Cafe[]> {
  // ...
}
```

```javascript
// ❌ WRONG: Never create new .js files in frontend/src/
// frontend/src/api.js - DON'T DO THIS
```

### Build Output

- `frontend/script.js` is a **generated bundle** (build artifact)
- Never edit `script.js` directly - it's compiled from TypeScript sources
- Always commit `.ts` files, not the bundled output

---

## Code Quality Tools

### Deno Lint (Automated Pattern Enforcement)

Lint and formatting tools are managed by **mise** (see `.mise.toml` `[tools]` section).

```bash
# Lint all TypeScript sources
mise run js:lint

# Auto-fix issues when possible
deno lint frontend/src/ --fix
```

**Lint Rules Enforced:**
- `no-explicit-any` - No `any` types
- `prefer-const` - Prefer `const` over `let`
- `no-var` - No `var` declarations
- `no-unused-vars` - Remove unused variables
- `require-await` - Mark async functions that don't use await
- `no-console` - No `console.log` (use `warn`/`error` only)
- `no-debugger` - No `debugger` statements
- `eqeqeq` - Use `===` and `!==` always

### Type Checking

```bash
# Strict type check with Deno (managed by mise)
mise run ts:check

# Full check (lint + format + type)
mise run js:check
```

### Formatting

```bash
# Format with Deno fmt (100 char width, 2-space indent)
mise run js:format
```

---

## Reactivity Pattern: Signals (Lightweight State Management)

For growing complexity, use the Signals pattern (SolidJS/Vue Ref style) instead of manual DOM manipulation.

### Installation

```bash
cd frontend
npm install @preact/signals-core
```

### Usage Example

```typescript
import { signal, computed, effect } from "@preact/signals-core";

// Create reactive state
const cafes = signal<Cafe[]>([]);
const filters = signal({ query: "", roast: "", roasterId: "" });
const isLoading = signal(false);
const error = signal<string | null>(null);

// Computed values (auto-updates when dependencies change)
const filteredCafes = computed(() => {
  return cafes.value.filter(cafe => {
    if (filters.value.query && !cafe.name.includes(filters.value.query)) return false;
    if (filters.value.roast && cafe.roast_level !== filters.value.roast) return false;
    return true;
  });
});

// Side effects (auto-runs when signals change)
effect(() => {
  console.log(`Found ${filteredCafes.value.length} cafes`);
  // Automatically re-renders when filteredCafes changes
  renderResults(filteredCafes.value);
});

// Update state (triggers reactivity)
async function loadCafes() {
  isLoading.value = true;
  error.value = null;
  try {
    cafes.value = await fetchCafes(filters.value);
  } catch (err) {
    error.value = "Failed to load cafes";
  } finally {
    isLoading.value = false;
  }
}
```

### Benefits Over Current Pattern

| Current Pattern | Signals Pattern |
|----------------|-----------------|
| Manual `renderResults()` calls | Auto-updates via `effect()` |
| Global variables (`mapIsVisible`) | Encapsulated signals |
| Imperative DOM updates | Declarative reactivity |
| Hard to track state changes | Clear data flow |

### When to Use Signals

**Use Signals when:**
- Multiple components depend on the same state
- State changes frequently (search input, filters)
- You need computed/derived values
- Manual DOM updates become hard to maintain

**Don't use Signals when:**
- Simple one-off DOM manipulation
- Static content
- The overhead isn't justified

---

## Project Structure

```
frontend/
├── src/
│   ├── main.ts          # Entry point
│   ├── api.ts           # API calls
│   ├── map.ts           # Map logic
│   ├── ui.ts            # UI rendering
│   ├── dropdowns.ts     # Dropdown logic
│   ├── types.ts         # TypeScript types
│   └── signals.ts       # (Optional) Reactive state
├── index.html
├── input.css            # Tailwind input
├── tsconfig.json        # TypeScript config
├── .eslintrc.json       # ESLint rules
└── script.js            # Generated bundle (DO NOT EDIT)
```

---

## Development Workflow

```bash
# Start development (hot-reload enabled)
mise run dev

# Run all checks before commit
mise run js:check

# Production build
mise run build:prod

# Clean build artifacts
mise run clean
```

---

## Common Patterns

### Safe DOM Element Access

```typescript
// ✅ Use type assertions with null checks
const btn = document.getElementById("my-btn") as HTMLButtonElement | null;
if (!btn) return;

// ✅ Or use optional chaining
document.getElementById("my-btn")?.addEventListener("click", handler);
```

### Event Debouncing

```typescript
let timer: ReturnType<typeof setTimeout>;
input.addEventListener("input", () => {
  clearTimeout(timer);
  timer = setTimeout(loadCafes, 300);
});
```

### Error Handling

```typescript
try {
  const data = await fetchCafes(filters);
  renderResults(data);
} catch (err) {
  console.error("Failed to load:", err);
  showErrorState();
}
```

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feat/my-feature

# Make changes to .ts files
# Run checks
mise run js:check

# Commit (script.js is auto-generated)
git add frontend/src/
git commit -m "feat: add new feature"

# Push
git push origin feat/my-feature
```

**Note:** `script.js` should be committed as it's the production bundle, but always regenerate from sources.
