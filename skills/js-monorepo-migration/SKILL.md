---
name: js-monorepo-migration
description: "Use when converting a JS/TS repo to a pnpm monorepo."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [monorepo, pnpm, workspace, refactor, packages, vite, typescript]
    related_skills: [js-toolchain-migration, framework-migration, github]
---

# JS/TS Monorepo Migration (pnpm workspaces)

Convert a single-package JS/TS repo into a pnpm workspaces monorepo: extract shared/util code into `packages/*` (importable by package name), keep the app under `apps/*` (or root), and prove typecheck/build/test/lint still pass. Deliverable is a working repo + PR, not a plan.

## When to Use

- A repo has accumulated a mix of pure utilities, React/library wrappers, and domain-specific code in one place (e.g. a fat `utils/` dir) and the user wants them split into workspace packages.
- Any "extract X into its own package(s)" on a pnpm repo.

## Procedure

1. **Map the split before moving anything.** Classify the code by COUPLING, not by directory name: pure utilities (no React/lib deps) vs library/React/browser-API wrappers vs domain-specific. Determine each group's external deps with a grep over imports:
   ```
   grep -rhoE "from ['\"][a-z@][^'\"]*['\"]" <dir> --include='*.ts' --include='*.tsx' \
     | grep -vE "from ['\"](\\.|@/)" | sort | uniq -c
   ```
   Confirm with the user before executing: package granularity, names/scope, app location (`apps/web` vs stay at root), publish policy (internal-only → `private:true` + `workspace:*`), delivery mode (buildless source vs built). These are cheap to ask and expensive to redo.

2. **Prove dependency direction is already clean.** `grep -rlE "from ['\"](@/src|\\.\\./.*src)['\"]" <dir>` must be empty — the code to extract must not import the app. A back-dependency means fix that first; extraction is only mechanical when the direction is one-way.

3. **Move with `git mv`, not `mv`** (preserves history; `--follow`/blame keep working). Create target dirs first. A moved file whose content also changes may show as delete+add (D+A) instead of rename (R) when similarity drops — cosmetic, history still follows.

4. **Write configs.** Root `package.json` becomes a thin orchestrator (scripts delegate via `pnpm --filter <pkg>`; keep shared tooling — typescript/vitest/oxlint/oxfmt/husky — at root). `pnpm-workspace.yaml`: `apps/*`, `packages/*`. `tsconfig.base.json` (shared compilerOptions) + per-package `tsconfig.json` extending it + root `tsconfig.json` (`include: ["apps", "packages"]`). Per-package `package.json` + barrel `index.ts`.

5. **Buildless internal source packages (default for internal-only).** Each package: `private:true`, `"main": "./index.ts"`, `"types": "./index.ts"`, and NO `exports` field. An `exports` map RESTRICTS deep subpath imports to its keys; with no `exports`, `moduleResolution: bundler` falls back to filesystem resolution so `@pkg/array` → `array/index.ts` resolves through the pnpm symlink. Never add a bare `"exports": {".": ...}` — it blocks deep imports.

6. **Rewrite imports by script, not by hand.** Regex over quoted specifiers with a classification map (first path segment → package). Three patterns: `@/utils/X` → `@pkg/X`, `@/src/X` → `@/X` (repoint the alias), `(../)+utils/X` → `@pkg/X`. See Pitfalls — especially cross-package relative imports that don't contain the dir name.

7. **Redistribute dependencies to where they're used.** Re-grep external imports per new package and move `react`/`three`/etc into the package that imports them; the app keeps only what it imports directly. Types are separate — see Pitfalls.

8. **`pnpm install`, then verify symlinks.** Workspace packages symlink into each CONSUMER's `node_modules/@scope/pkg` (e.g. `apps/web/node_modules/@utils/core`), NOT into root `node_modules/@scope/` unless root declares them. TS/Vite resolve `@pkg/deep/import` by walking up from the importing file to the nearest `node_modules/@pkg` symlink.

9. **Verify the full pipeline.** `typecheck`, `build`, `test`, `lint`, `format:check` all exit 0 (warnings-only lint is fine).

10. **Deliver.** Push a branch + open a PR — confirm with the user before pushing (external upload). Note deploy-config changes (e.g. Vercel Root Directory → `apps/web`).

## Pitfalls

- **`@types/*` must be declared in EVERY package that uses the library, not just the app.** pnpm does not hoist them to root; a package with `.tsx` but no `@types/react` fails typecheck with "Could not find a declaration file for module 'react'". Add `@types/react`/`@types/react-dom`/`@types/three` as devDeps to each package containing React/three code. `@types/node` at root is enough for a shared `types: ["node"]` because root devDeps resolve from any package's walk-up.

- **Cross-package relative imports hide from naive rewrite scripts.** A regex matching `(../)+utils/` misses `../api` (a hop from `utils/apis/crypto.ts` to `utils/api`) because the dir name `utils` isn't in the path; after the move that `../api` lands in a DIFFERENT package and breaks. Grep each new package for `from '\.\./...'` and confirm every relative hop still lands in the SAME package; rewrite crossers to the package name (`@utils/core/api`).

- **Within-package self-imports: use relative paths, not the package's own name.** `@pkg/foo` from inside `@pkg` relies on self-reference resolution (pnpm self-link + bundler), fragile without an `exports` field. Convert `@/utils/object/object` → `../object/object` when both files land in the same package.

- **Don't rewrite same-directory `./utils/...` paths — only `(../)+utils/`.** Apps often have a LOCAL `./utils/` module (e.g. `src/shared/modules/fluids/utils/createFbos`) unrelated to the top-level `utils/` being extracted; rewriting `./` paths corrupts them.

- **The format-glob change pulls config files into the formatter.** The old `format` script ran over `src utils` (no JSON); after the move it becomes `packages apps`, and oxfmt with `useTabs:true` reformats `package.json`/`tsconfig.json`/`vercel.json` with TABS. Add `**/*.json` to the formatter `ignorePatterns` (or scope the glob to `{ts,tsx}`). If JSON was already mangled, re-indent it to 2-space but scope that script NARROWLY — a repo-wide `json.dump` rewrites unrelated files like `.claude/settings.json`; revert those.

- **Repoint every build-time reference, not just source imports.** `vite.config.ts` imports `utils/apis/config` (relative) and carries an `@` alias to the repo root plus a `@chroma-core/default-embed` alias into `utils/` — all need repointing when the app moves. After the move, grep the whole repo (not only `src/`) for `utils/` and `src/` leftovers.

- **Prove a surfaced test failure is pre-existing before chasing it as a regression.** Isolate with a minimal repro outside the moved code. `new (vi.fn().mockImplementation(() => X))()` throws "not a constructor" on vitest 4.x + node 26 — a pre-existing mock-pattern issue (the mock implementation must be a `function`, not an arrow, to be `new`-able). Untouched files failing identically = not your regression; report it, don't fix it inline.

- **Moving the app under `apps/*` breaks Vercel unless the output dir is repointed.** Vercel defaults Root Directory to the repo root and looks for `dist` there; after the move Vite writes to `apps/web/dist`, so deploys fail with `STATIC_BUILD_NO_OUT_DIR`. Fix without dashboard access: add a root `vercel.json` with `installCommand`/`buildCommand`/`outputDirectory` (e.g. `pnpm install`, `pnpm --filter @utils/web build`, `apps/web/dist`), carry over the SPA `rewrites` + security `headers` from the app's old vercel.json, and delete the app-level copy. Setting Root Directory = `apps/web` in the dashboard is the equivalent alternative.

- **Agent-instruction files (AGENTS.md, `.agents/`) are write-protected in Hermes.** A blocked write must not be retried via another path. After moving dirs, these files still reference old paths — flag them for the user to approve or update rather than force-writing. When the rewrite is approved, write the doc in the user's language (full Japanese for this user — a mixed-language draft got corrected to full Japanese).
