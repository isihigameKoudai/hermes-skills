---
name: framework-migration
description: "Use when porting a website to a new framework or stack."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [migration, replatform, Astro, SSG, Nuxt, Vue, verification]
    related_skills: [frontend-framework-security, github-pr-workflow]
---

# Framework Migration (preserve appearance)

Port an existing website from one framework/stack to another (e.g. Nuxt2/Vue2 → Astro SSG) while keeping the rendered UI pixel-identical and behavior intact. Covers recon, tech selection, the port, and the proof that nothing changed.

## When to Use

- Migrating a live site to a new framework/SSG (e.g. Nuxt→Astro, Vue→SvelteKit) with the requirement that the rendered UI stays identical.
- Re-platforming while keeping the same domain/hosting, or moving to a new host.
- Replacing framework state/effects (Vuex, reveal-on-scroll, jQuery smooth-scroll) with equivalent minimal JS.

Support: `scripts/compare-site.cjs` — normalized text/img/href diff of the built site against live production.

## Procedure

1. **Recon — read everything, then fetch the live site.**
   - Clone the repo and read every page, component, style, and config file.
   - `curl -sI` the live site for the host + render mode (`server:` header, `data-server-rendered="true"` in HTML).
   - `curl -sL` every page and save to disk for later diffing. A trailing-slash 301 reveals the canonical URL scheme.
   - Inventory every feature that must survive: forms (where do they POST?), analytics, PWA/manifest/service-worker, scroll/reveal/modal behavior, env vars.

2. **Tech selection — recommend, then get a decision if the fork is real.** Framework and hosting are two separate axes; present a comparison table and a recommendation, then confirm. Do not silently pick.

3. **Port.**
   - Consolidate ALL component styles into ONE global stylesheet. Scoped styles (Vue `scoped`, Astro's default scoping) rewrite selectors/specificity and drift the look; global keeps selectors identical.
   - Copy markup and text verbatim, including exact `<title>`, meta/og/twitter tags.
   - Serve static assets from identical root paths (`public/` → `/img/...`, `/svg/...`).
   - Replace framework state (Vuex/Pinia) with plain module JS when the state is simple (modal toggle, form fields).
   - Preserve the canonical URL scheme (trailing slash or not) to match the host's pretty-URLs behavior.
   - For forms posting to a secret webhook, proxy through a serverless function instead of shipping the URL to the browser.

4. **Verify against live** (see `scripts/compare-site.cjs`).
   - Serve the build; curl every page for 200 and a missing path for 404.
   - Run the normalized text/img/href diff against the live HTML. Every diff must be EXPLAINABLE: hidden/conditional elements, image URL-scheme change (same files), trailing-slash links.
   - Confirm CSS compiled equivalently — minifiers rewrite `translateX(-50%)`→`translate(-50%)`, `translate(0,y)`→`translateY(y)`, and color formats; these are safe equivalents, not drift.

5. **Deliver** — build, then push (a branch on the existing repo is the default for a re-platform; confirm the target first).

## Rules

- "Unchanged appearance" means reproduce pre-existing visual bugs faithfully, then flag them — a silent fix makes the new site DIFFER from live and violates the constraint. Offer the fix separately.
- SSR→SSG yields identical HTML only when content is fully static. Confirm no dynamic data before choosing SSG; for a static portfolio/landing it is strictly simpler.
- Omit the initial `src` on a JS-populated modal `<img>` — `src=""` triggers a wasted fetch in some browsers; set src in the show handler.

## Astro gotchas

- A `<script>` (non-inline) in a Layout is bundled and INLINED into each page when small (~<4KB). Verify with `grep -c '<script type="module">' dist/*/index.html`, not by hunting for a `.js` in `dist/_astro/`.
- `import.meta.env` only exposes `PUBLIC_`-prefixed vars to the client. To stay compatible with an existing env var name, read both: `import.meta.env.PUBLIC_X || process.env.X` (both resolve at build time in frontmatter).
- `npm audit` flags on `sharp` (libvips) are transitive and unused when serving plain `<img>` from `public/` (no astro:assets Image). Do NOT `npm audit fix --force` — it jumps a major Astro version.

## Netlify gotchas

- With `"type": "module"` in package.json, functions run under the Web-standards (v2) runtime: handler is `export default async (req) => Response` and MUST return a `Response` — the legacy `{ statusCode, body }` object throws `NetlifyUserError: Function returned an unsupported value`. Test locally by importing the handler and calling it with `new Request(url, { method, body })`; assert `.status` and `await .text()`.
- Functions are served at `/.netlify/functions/<name>` (leading dot). A client `fetch('/netlify/functions/<name>')` (no dot) silently hits the 404 page. Verify after build (`grep -oE 'fetch\("/[^"]*' dist/<page>/index.html`) and after deploy (`curl -s <site>/<page>/ | grep -oE 'fetch\("/[^"]*'`).
- Deploy propagates in ~30–60s; a transient 500 from the upstream (e.g. Slack) can appear on the first cold call — re-test before assuming a code bug.

## Pitfalls

- The terminal/JSON transport double-escapes newlines: a file showing `\\n` in tool output is a single backslash+n in the file, i.e. a real JS newline escape. Confirm with `od -c` before porting string-building code.
- Merging per-component scoped styles can make shared class names collide (e.g. two `.logo-wrapper` with different widths). Disambiguate the diverging variant with a modifier class (`.logo-wrapper.wide`) instead of letting the later rule win silently.
