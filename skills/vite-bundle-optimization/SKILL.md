---
name: vite-bundle-optimization
description: Use when shrinking a Vite/React bundle via code splitting.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vite, react, bundle-size, code-splitting, performance, tanstack-router]
    related_skills: [js-toolchain-migration, js-monorepo-migration, plan]
---

# Vite / React Bundle Optimization

Procedure for cutting a bloated single-chunk Vite+React app down to a small initial load. The dominant cause is almost always the same: routes statically import their page components, so the bundler has no dynamic-import boundary to split on, and every heavy dependency lands in the entry chunk.

## When to Use

- A Vite/React app (or pnpm monorepo with a Vite app) has a bloated production bundle — single large chunk, the `>500 kB` warning, or a slow initial load.
- The app uses TanStack Router (file-based routes) and you want route-level code splitting without hand-writing `React.lazy` per route.

## Workflow

1. **Measure the baseline before touching anything.** Run the production build and read the chunk table — you will claim the improvement against these numbers, so they must be real, not guessed.
   ```bash
   pnpm build   # or pnpm --filter <app> build
   ```
   One `index-*.js` in the MB range plus the `(!) Some chunks are larger than 500 kB` warning = everything bundled into one chunk. Record minified AND gzip sizes.

2. **Find the root cause, don't assume.** Grep the route files: `grep -rn "createFileRoute" src/routes`. Static `component: SomePage` imports mean no splitting. Confirm which heavy deps (three, @mediapipe/tasks-vision, @google/genai, chromadb, recharts, lightweight-charts) are reached from those routes. Also check whether anyone imports a top-level package barrel — deep imports (`@utils/modules/i-state`) tree-shake; a barrel `export *` that re-exports a heavy module pulls the whole chain in.

3. **Enable route-level code splitting (TanStack Router).** Add `autoCodeSplitting: true` to the `TanStackRouterVite({...})` plugin options in `vite.config.ts`. This is the canonical flag (not `experimental.enableCodeSplitting`); it transforms each file route's component/loader into a lazy `import()`, producing per-route chunks.
   - PITFALL — plugin order: with `autoCodeSplitting` on, the TanStack Router plugin MUST come before `@vitejs/plugin-react`. Otherwise the build dies with `Plugin order error: '@vitejs/plugin-react' is placed before '@tanstack/router-plugin' ... must come BEFORE JSX transformation plugins`. Reorder to `plugins: [TanStackRouterVite({...}), react()]`.

4. **Lazy-load named-export components with the right argument.** `lazyRouteComponent(importer, exportName)` — the second arg is the named export. Wrapping a module whose component is a NAMED export in `lazyRouteComponent(() => import('...'))` alone looks for a `default` export and fails at runtime. Verify the installed package's actual export shape first (`grep export node_modules/.../dist/esm/index.d.ts`), then pass the name explicitly:
   ```ts
   lazyRouteComponent(() => import('@tanstack/router-devtools'), 'TanStackRouterDevtools')
   ```

5. **Strip dev-only code from production.** Gate devtools (and any dev-only component) behind `import.meta.env.DEV` so they are tree-shaken out of the prod bundle — a lazy devtools chunk still ships ~60 kB if left unconditional.

6. **Re-measure and confirm the split.** Rebuild and read the chunk table again. Heavy libs should now be isolated per-route chunks (e.g. `three.module` ~700 kB, `gemini-embedding` with genai+chromadb, `summary` with recharts). The initial `index` chunk should drop to the app shell — React + Router + shared utils (~100 kB gzip or less). A remaining >500 kB chunk that is a single library now loaded on demand is acceptable; do not chase it.

## Pitfalls

- Replacing `tsc` with `tsrs` in a build script is only safe if `noEmit` is set in tsconfig (then `tsc` was pure typecheck, not emitting). If the repo already runs `tsrs --noEmit --fast` for `pnpm typecheck`, `tsc && vite build` is double-typechecking — a swap to `tsrs --noEmit --fast && vite build` is tempting. BUT: `tsrs` ships a native binary (`@tsrs/linux-x64-gnu`) that requires glibc 2.34+ — on deployment platforms with older build images (Vercel etc.) it fails at build time. Before swapping, grep existing docs/commit history for a documented decision to keep `tsc` in `build` (a repo may have deliberately kept `tsc` for portability); if found, leave `build` alone and keep `tsrs` only for dev `pnpm typecheck`. The ~12s build-time win is not worth breaking the production build.
- Before claiming a test failure is yours, run `git status --short` / `git diff --stat`. Failures in source files you never touched (e.g. a broken `AudioContext` mock) are pre-existing, not a regression from your change — report them as such instead of chasing them.
- Don't optimize a library warning into a rewrite: `Module "node:process" has been externalized for browser compatibility` (chromadb etc.) is informational once the lib is isolated to its own lazy chunk; the initial-load impact is already gone.
