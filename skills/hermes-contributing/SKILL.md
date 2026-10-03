---
name: hermes-contributing
description: "Use when contributing PRs to NousResearch/hermes-agent."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes-agent, contributing, pr, open-source, github]
    related_skills: [hermes-agent]
---

# Contributing to Hermes Agent

## When to Use

Use when the user wants to contribute a PR to NousResearch/hermes-agent (finding an issue, fixing a bug, adding a feature, or shipping docs). For code mechanics (project layout, adding tools/slash commands, the agent loop) load the bundled `hermes-agent` skill and its `references/contributor-guide.md`; this skill covers the strategy and the hard gates.

## Entry-point strategy (for building a track record)

- There is NO `good first issue` or `help wanted` label. Don't search for one.
- Newcomers start at P2 bugs (thousands open; "workaround exists" severity, repro steps usually in the issue). P0/P1 already have fix PRs in flight — competing there wastes the effort.
- CONTRIBUTING.md ranks contributions: bug fixes → cross-platform → security → perf/robustness → skills → tools → docs. Bug fixes merge most reliably and carry the most weight.
- Docs fixes (`website/`, Docusaurus) are the lowest-friction first merge. Ship one docs PR to get the first merge through, then move to bugs.

## Hard gates — a PR gets rejected if these are missed

- Python is pinned to `>=3.14,<3.15`; Node `^22.22.0` / `^24.11.0` / `>=26`.
- Any new PyPI dependency must carry a `<next_major` upper bound: `pkg>=1.2,<2` for post-1.0, `pkg>=0.29,<0.32` (≈ current minor +2) for pre-1.0. Unbounded `>=X` specs are rejected outright.
- Search both open AND merged issues/PRs before starting — duplicates get rejected at review time, after the work is done. `gh search issues/prs --state all`. Also grep the source: the tracker lags the code, and many "features" already ship in-tree.
- For larger work, comment on the issue to claim it first so others don't start the same thing.

## Placement rules (what does NOT go in-tree)

- Prefer a skill over a new tool; new tools are "rarely needed".
- Memory providers and third-party product integrations must ship as standalone plugins, never as a new dir under `plugins/memory/` or `plugins/`. Such PRs are closed with a pointer to publish a separate repo.

## Dev environment

- Activate the PM dev env from repo root each shell: `source ./activate` (fish: `source ./activate.fish`); it provisions Python 3.14 and hides the global `hermes`. Never raw pip/uv.
- Run `scripts/run_tests.sh tests/<path>/` for CI parity (clears creds, TZ=UTC, per-file subprocess, no xdist).
- Conventional Commits `type(scope): ...` — types fix/feat/docs/test/refactor/chore, scopes like cli/gateway/tools/cron/skills/agent/install.
- Branch naming: `fix/…`, `feat/…`, `docs/…`, `test/…`, `refactor/…`.
