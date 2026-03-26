# Technical SEO Audit — Ache o Café

**Date:** 2026-03-26
**Branch:** seo-fix
**Overall Score:** 32/100

---

## Category Scores

| Category | Status | Score |
|----------|--------|-------|
| Crawlability | fail | 20/100 |
| Indexability | warn | 45/100 |
| Security | fail | 15/100 |
| URL Structure | warn | 60/100 |
| Mobile | pass | 85/100 |
| Core Web Vitals | warn | 55/100 |
| Structured Data | fail | 0/100 |
| JS Rendering | fail | 30/100 |
| IndexNow | fail | 0/100 |

---

## Critical Issues

### [ ] 1. No robots.txt
No `robots.txt` at domain root. nginx returns 404, which some crawlers interpret as "block all."

**Fix:** Create `frontend/robots.txt`:
```
User-agent: *
Allow: /
Sitemap: https://YOUR_DOMAIN/sitemap.xml

User-agent: GPTBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Bytespider
Disallow: /
```

---

### [ ] 2. No XML sitemap
No sitemap declared. Googlebot has no signal about URLs or last-modified dates.

**Fix:** Create `frontend/sitemap.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://YOUR_DOMAIN/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

---

### [ ] 3. All content is client-side rendered (CSR)
Every café listing is fetched via `fetch()` in `script.js`. Initial HTML sent to Googlebot is an empty `#results-list`. Google must execute JS to see any café content — delays indexing by days, increases risk of content being missed.

**Fix options (pick one):**
- **Option A (recommended):** Add server-side rendering at the API layer — return a pre-rendered HTML list on first load.
- **Option B (quick win):** Add a `<noscript>` fallback linking to a static list page.
- **Option C:** Implement dynamic rendering (serve pre-rendered HTML to bots, CSR to users).

---

### [ ] 4. No HTTPS — Dockerfile exposes port 80 only
HTTPS is a confirmed Google ranking signal. Without it Chrome shows "Not Secure."

**Fix:** Add TLS termination — either via a reverse proxy (nginx/Caddy in front of the container) or configure SSL in the nginx stage of the Dockerfile.

---

### [ ] 5. No structured data
Zero JSON-LD. Missing `LocalBusiness`, `Product` (beans), `WebSite`/`SearchAction` schemas → no rich results eligibility.

**Fix:** Add to `<head>` in `index.html`:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Ache o Café",
  "url": "https://YOUR_DOMAIN/",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://YOUR_DOMAIN/?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
</script>
```

---

## High Priority

### [ ] 6. No `<meta name="description">`
Google will auto-generate a snippet from CSR content (which may be empty).

**Fix:** Add to `<head>`:
```html
<meta name="description" content="Descubra os melhores cafés especiais do Brasil. Filtre por torra, torrefação e perfil sensorial." />
```

---

### [ ] 7. No canonical tag
Without it, `http://`, `https://`, `www.`, and non-`www.` are treated as separate pages.

**Fix:** Add to `<head>`:
```html
<link rel="canonical" href="https://YOUR_DOMAIN/" />
```

---

### [ ] 8. No Open Graph / Twitter Card tags
Social shares and AI crawlers (PerplexityBot, ChatGPT-User) use OG tags to generate previews.

**Fix:** Add to `<head>`:
```html
<meta property="og:title" content="Ache o Café | Descubra Cafés Especiais" />
<meta property="og:description" content="Descubra os melhores cafés especiais do Brasil." />
<meta property="og:type" content="website" />
<meta property="og:image" content="https://YOUR_DOMAIN/og-image.jpg" />
<meta property="og:url" content="https://YOUR_DOMAIN/" />
<meta name="twitter:card" content="summary_large_image" />
```

---

### [ ] 9. Journal hero image not preloaded (LCP risk)
The Unsplash background image is the likely LCP element on desktop. As a CSS `background-image` it is invisible to the browser's preload scanner.

**Fix:** Add to `<head>`:
```html
<link rel="preload" as="image"
  href="https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=1200&q=80" />
```

---

### [ ] 10. `font-display: block` on Material Symbols blocks rendering
Blocks ALL render until the icon font loads (FOIT). Hurts LCP and CLS. Googlebot sees blank icon placeholders.

**Fix:** Change URL parameter in `index.html`:
```html
<!-- from -->
&display=block
<!-- to -->
&display=optional
```
`optional` shows icons only if font loads within 100ms, otherwise hides them — no layout shift, no render block.

---

### [ ] 11. No security headers in nginx
Default nginx ships with none of: `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy`.

**Fix:** Add to `Dockerfile` nginx stage or a custom `nginx.conf`:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
gzip on;
gzip_types text/css application/javascript application/json image/svg+xml;
```

---

## Medium Priority

### [ ] 12. No AI crawler policy in robots.txt
Covered by item #1. Once robots.txt is added, decide on AI crawler stance (see fix in item #1).

---

### [ ] 13. Mixed-language `<title>`
`html lang="pt-BR"` but title is `"Ache o Café | Specialty Coffee Discovery"`. Confuses language detection.

**Fix:**
```html
<title>Ache o Café | Descubra Cafés Especiais do Brasil</title>
```

---

### [ ] 14. No `<link rel="preconnect">` for backend API
DNS + TCP handshake overhead on first fetch. Once the API is on a real domain:

**Fix:** Add to `<head>`:
```html
<link rel="preconnect" href="https://api.YOUR_DOMAIN" />
```

---

### [ ] 15. No `<meta name="theme-color">`
**Fix:**
```html
<meta name="theme-color" content="#271310" />
```

---

## Low Priority

### [ ] 16. Stale copyright year
`© 2024 Ache o Café` in footer. Update to current year or make dynamic.

### [ ] 17. `href="#"` on footer links
Dead links waste crawl budget. Replace with real URLs or remove `href` attribute.

### [ ] 18. IndexNow not implemented
Bing, Yandex, and Naver support IndexNow for near-instant indexing. Low effort, high value for non-Google engines. Implement via a POST to `https://api.indexnow.org/indexnow` on content changes.

---

## Implementation Order

1. `robots.txt` + `sitemap.xml` (files, no code change)
2. `<head>` meta tags: description, canonical, OG/Twitter, theme-color
3. JSON-LD structured data
4. LCP preload + font-display fix
5. nginx security headers + gzip
6. Title language fix + footer year
7. CSR → SSR (larger effort, separate planning)
8. IndexNow (requires backend hook on data changes)
