---
name: js-toolchain-migration
description: "Use when migrating JS/TS lint/format/typecheck tooling."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [migration, lint, formatter, typecheck, oxlint, oxfmt, tsrs, biome, eslint, prettier, pnpm]
    related_skills: [github-pr-workflow, framework-migration]
---

# JS/TS Toolchain Migration (linter / formatter / typechecker)

Swap one lint/format/typecheck toolchain for another (biome → oxlint+oxfmt+tsrs, eslint+prettier → biome, etc.) and prove the before/after speed with real numbers. The deliverable is a PR with the new tooling wired into scripts + pre-commit, existing disable comments converted, and a benchmark doc — not just the packages installed.

## When to Use

- Replacing a linter/formatter/typechecker (biome, eslint+prettier, tsc) with faster or stricter alternatives, especially Rust-native tools (oxlint, oxfmt, tsrs).
- Any swap where the user wants a before/after speed benchmark committed as a doc.
- Any time a repo's lint/format/typecheck `package.json` scripts and pre-commit hooks must be rewired to new tooling.

## Procedure

1. **Recon the current setup.** Read `package.json` (scripts, devDeps, `lint-staged`), the linter/formatter config, tsconfig(s), pre-commit hooks, and CI/workflow files. Note the file scope the old tool actually ran over (e.g. `biome check src utils` — scoped to two dirs, not the whole repo).

2. **Benchmark BEFORE, before uninstalling the old tool.** Use `hyperfine --warmup N --runs N` and wrap every command the same way (e.g. `pnpm exec <tool>`), so pnpm startup overhead is in all numbers equally. Capture lint, format-check, and typecheck separately; the typecheck is usually the headline (a pure-JS `tsc` vs a Rust port can be 6×+).

3. **Swap packages.** `pnpm remove <old>` then `pnpm add -D <new...>`. If pnpm 12 blocks a new package with a supply-chain error, see Pitfalls.

4. **Migrate config, prefer a built-in migrator.** `oxfmt --migrate=biome` (and `--migrate=prettier`) generates `.oxfmtrc.json` from the old config automatically. For the linter, write `.oxlintrc.json` by hand: map the old rule customizations 1:1 and enable type-aware where asked (`options.typeAware: true`). See `references/biome-to-oxc.md` for the biome→oxlint/oxfmt rule and option mapping.

5. **Convert disable comments.** Every `// <tool>-ignore` / `{/* <tool>-ignore */}` must become the new tool's disable (`// oxlint-disable-next-line <rule> -- reason`), or the previously-suppressed diagnostics resurface AND the old comments go dead. Do it with a regex script over the file tree (map group/rule → new rule; delete comments whose rule has no equivalent), not by hand. Verify with `--report-unused-disable-directives`: "unused" means a wrong rule name or a redundant stacked comment.

6. **Wire scripts + pre-commit.** Update `lint`/`format`/`typecheck` scripts and `lint-staged`/husky. Keep the format step scoped to the SAME files the old tool handled (Pitfalls: formatter scope creep).

7. **Verify the full pipeline.** Run `lint`, `format:check`, `typecheck`, AND `build` to exit 0. Then push, open the PR, and watch the deploy/CI check — a native-binary tool that ran fine locally can fail on the CI/deploy image (Pitfalls).

8. **Benchmark AFTER + write the doc.** Same hyperfine settings; put a before/after table (per-step + end-to-end total) in a committed `.md`, with tool versions, machine spec, and warmup/runs.

## Pitfalls

- **Native (Rust) tool binaries can demand a glibc/arch newer than the deploy image.** They download fine but fail at EXECUTION, not install — so `pnpm install` looks healthy while the build dies. Before wiring a native binary into the production `build` or CI path, check `objdump -T <binary> | grep -oE 'GLIBC_[0-9.]+' | sort -V | tail -1`. If it exceeds the deploy image's glibc (e.g. tsrs needs 2.34, Vercel/older images don't have it), keep the production `build` on the pure-JS fallback (`tsc`) and use the fast tool only in a dev-only script (`typecheck`). Verify against the OLD commit's deploy status: main succeeding while the PR fails points at the newly-executed native binary.

- **Auto-fixers can rewrite valid code into a type error — do not auto-fix lint on commit without a typecheck gate.** `oxlint --fix`'s `unicorn/no-useless-spread` fixer turns `[...new Array(n)]` into `new Array(n).fill()`, which is TS2554 because `Array.fill` requires a value arg — runtime-equivalent but type-broken. In a repo with no CI typecheck this lands silently. Keep pre-commit hooks to safe formatters (`oxfmt --write`) + check-only lint (`oxlint`, no `--fix`); run `tsc`/`tsrs` after any manual `--fix`.

- **Prettier-compatible formatters format MORE file types than biome did (markdown, html, yaml).** oxfmt/prettier touch `.md`/`.html`/`.yaml` that biome never formatted, ballooning the migration diff with unrelated markdown reflow. Scope the `format` script to the old tool's dirs AND add `**/*.md`, `**/*.html`, `**/*.yaml`, `**/*.yml` to `ignorePatterns`. A formatter's `--check` on the whole repo can flag 60+ files while scoped to `src utils` only 1–4 — that difference is the scope creep, not your config.

- **oxlint type-aware linting needs a type backend installed** (`tsrs` or `oxlint-tsgolint`), enabled via `options.typeAware: true` in `.oxlintrc.json`. Without the backend, type-aware `typescript/*` rules silently don't run — don't claim type-aware coverage until the backend is present and type-aware rules actually fire.

- **pnpm 12 `trustPolicy: no-downgrade` blocks legitimately re-published tools** (a fast-moving beta shipped without provenance triggers "trust downgrade / possible package takeover"). Add the exact `name@version` to `trustPolicyExclude` in `pnpm-workspace.yaml` — the same fix the repo already applies to other packages. A strict `minimumReleaseAge` in the same file will silently pin you to an OLDER version of a fast-moving tool (it resolves the newest version older than the age threshold); the committed lockfile freezes that, so a `--frozen-lockfile` CI is consistent.

- **Rule coverage is not a 1:1 match across tools.** Enabling the mapped rules will surface NEW diagnostics (the new tool's rules are stricter in places) and some old rules have no equivalent (e.g. biome `performance/noAccumulatingSpread`). Count and compare before/after warning totals; expect some drift and say so in the PR rather than hiding it.
