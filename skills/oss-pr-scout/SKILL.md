---
name: oss-pr-scout
description: Use when shipping an upstream OSS PR from the user's stack.
---

# OSS PR scouting and shipping

Goal: from the libraries the user actually uses, pick an issue that is still open *and still unimplemented*, then ship a PR backed by real test output.

## 1. Build the stack list from evidence

Do not guess what the user uses. Pull `package.json` from their repos:

```sh
gh repo list <user> --limit 100 --json name,primaryLanguage,pushedAt
for r in <repos>; do gh api repos/<user>/$r/contents/package.json --jq '.content' | base64 -d; done
```

Rank candidates by: actively maintained, small reproducible bug, and a surface the user knows (React/Vue/Solid, Vite, TanStack, recharts, valibot, vanilla-extract...).

## 2. Duplicate check is two-step - do both or you will rewrite an existing PR

The label scan (`is:issue is:open label:"good first issue" label:bug no:assignee`) lies in both directions: many repos use no labels, and search rate-limits at 30 req/min (sleep 3-4s, retry 20s+ on "secondary rate limit").

Authoritative check per candidate:

```sh
gh api repos/OWNER/REPO/issues/N/timeline --paginate   # cross-referenced / connected PRs
gh pr list -R OWNER/REPO --state all --search "<issue keywords>"
```

The timeline alone misses PRs whose body never writes `#N` (seen with unjs/ofetch #637 -> PR #638). The title search alone misses PRs that reference the issue only in a commit. Run both, and also skim issue comments for "I'd like to work on this" / "Opened a fix: #NNNN".

Also check whether `main` already implements the request - fast-moving repos (recharts, TanStack) often have the fix merged while the issue stays open.

## 3. Implement in a fork, verify with the repo's own runner

```sh
gh repo fork OWNER/REPO --clone=false
git clone --depth=1 https://github.com/OWNER/REPO.git && cd REPO
git remote add fork https://github.com/<user>/REPO.git
```

Monorepo (pnpm) reality checks:
- Install scoped: `pnpm install --filter @scope/pkg... --ignore-scripts` (full install pulls examples and is huge).
- Workspace deps imported by source (e.g. `@tanstack/history`) need `pnpm --filter <dep> build` before vitest can resolve them.
- Run the package suite, not a single file: signature changes ripple into test stubs and benchmark baselines (`router.stores.location.get()`, frozen baseline hooks taking the old arity).
- Prove eslint noise is pre-existing: `git stash && npx eslint <files> && git stash pop`, compare problem counts.
- Typecheck explicitly (`npx tsc -p tsconfig.json --noEmit`) and build the package (`pnpm --filter <pkg> build`) before pushing.

## 4. PR body

State what changed, the additive/compat surface, exact local commands with their pass counts, and what was *not* run (e2e, browser suites) so CI is the stated source of truth. Link the issue with `Closes #N` only when the change fully resolves it.

## Pitfalls learned

- A maintainer comment saying "not supported, use this workaround" means the issue is a decision, not a bug - don't code against it.
- Don't ship docs that assert compiler/language-service internals you have not reproduced; `@vue/compiler-sfc` hoists `export type` out of a generic setup block while Volar's virtual file reports TS1184 - the two disagree, so a doc claim needs language-tools verification first.
- Issues that read like maintainer-authored task specs (`feat(...): expose ...`) are the best PR targets when no PR is linked; they already contain scope, tests and docs expectations.
- Keep one PR per repo per round; never batch unrelated fixes.
