---
name: frontend-framework-security
description: Use when assessing frontend framework security tradeoffs.
---

# Frontend Framework Security

## When to Use

- The user asks whether an architecture change (SSR→ISR, SSR→static, framework migration) reduces security risk, or whether a framework feature/rendering mode can do something (e.g. "can ISR/SSG regenerate only stale pages", "does Astro do this").
- The user asks to collect, assess, or verify framework vulnerabilities (CVE lists, advisories).

## Core principle: the boundary is "runtime server", not rendering mode

When the user asks whether an architecture change (SSR→ISR, SSR→static, framework migration) reduces security risk, answer on ONE axis: does a runtime server still execute request-time code?

- A running server (`next start`, platform serverless functions, adapters) keeps the whole runtime attack surface — Server Actions, RSC request deserialization, middleware, rewrites, `/_next/image` — regardless of whether pages are SSR or ISR.
- Only `output: 'export'` (pure static, no Node runtime) removes that surface. Every critical RCE in the modern framework era requires a running server, so pure static export is structurally immune to that class.
- ISR does NOT grant this immunity: ISR requires a running server (or Vercel/Netlify). "ISR + pure static hosting" is a contradiction — say so plainly rather than letting the user assume they keep both.

## Rendering modes and their security meaning

| Mode | Runtime server | ISR | Attack surface |
|---|---|---|---|
| Static export (`output:'export'`) | none | not supported | build-time + CDN + client only |
| Self-hosted ISR (`next start` + CDN) | yes | yes | ~same as SSR |
| ISR on Vercel/Netlify | platform functions | yes | platform mitigates some classes |

## Framework facts (verify against current docs before citing version numbers)

- Next.js `next build` has NO per-page skip — every static page re-renders each build. "SSG + rebuild only stale pages" is not native; the closest is a scheduled full rebuild + hash-based immutable deploy, where unchanged files keep their URL so only changed pages effectively swap in.
- Next.js ISR re-renders the WHOLE page, not a diff. "Incremental" = page-by-page, not differential. Triggers: (a) first request after `revalidate` expires (stale-while-revalidate), or (b) `revalidateTag()` / `revalidatePath()` on-demand.
- Next.js on-demand revalidation requires a Server Action/API route — it presumes an exposed server endpoint, so it deepens the server dependency, not removes it.
- Astro `experimental.incrementalBuild` skips re-rendering unchanged static pages at BUILD time (server-less) — the "SSG + only stale pages" answer Next.js lacks. Requires a per-page `cacheKey` from `getStaticPaths()` and persisting `node_modules/.astro/` between builds; only covers `getStaticPaths()` routes, and a wrong `cacheKey` silently serves stale pages.
- Astro has NO native per-page ISR (no `revalidate:N` export). ISR comes from adapters (Vercel `isr:true`, Netlify, EdgeOne) = a server. Same server caveat as Next.js.
- Static-export constraints to state: `revalidate`, Server Actions, middleware, rewrites, and default `next/image` optimization all require a server and are all lost under `output:'export'`. The security win is paid for by losing those features.

## CVE verification workflow

To collect or assess framework vulnerabilities, cross-check three sources and never trust blog roundups alone:
1. Vendor security advisory (nextjs.org/security blog, GitHub advisory GHSA-*).
2. NVD (nvd.nist.gov) for version ranges and CVSS.
3. CISA KEV for in-the-wild exploitation status.

Pitfall: blog roundups conflate CVEs. A pentest vendor attributed the `x-middleware-subrequest` middleware bypass to CVE-2024-43481 (which is actually a Microsoft Windows Task Scheduler privilege-escalation CVE); the real one is CVE-2025-29927. When a blog's CVE number looks off, verify the CVE number itself before trusting the writeup. The user requires every claim verified against official docs and misinformation called out explicitly — name the wrong source and the correct CVE.

## Recurring vulnerability classes (structural — refresh specific CVEs from the vendor advisory before citing)

- **Middleware auth/authorization bypass** — recurs (pathname/i18n, `x-middleware-subrequest`, Turbopack single-locale). Root cause: auth placed only in middleware, nothing behind the routing layer.
- **Cache poisoning** — the largest recurring theme, across Pages/App Router/ISR/RSC/Image Optimization/`fetch`. This class specifically targets SSG/ISR/CDN caches, so going static/ISR does NOT eliminate it; it moves to CDN cache-key hygiene. Managed platforms (Vercel/Netlify) mitigate at the edge.
- **Server Actions / RSC SSRF and DoS** — the newer attack surface; SSRF via `Host` header or forwarded headers, DoS via hanging requests or CPU exhaustion.
- **Runtime RCE** — RSC Flight protocol deserialization (React2Shell), image-optimization libraries (sharp/librsvg SVG), `use cache`. All require a running server → structurally immune under pure static export.
