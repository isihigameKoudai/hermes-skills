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
- An open issue is not the same as an unclaimed issue. Verify it's unclaimed (next section) BEFORE recommending it — recommending a bug whose fix PR already exists wastes the user's time.
- `needs-decision` + `P3` on a feature issue means parked awaiting a maintainer call (no assignee, no milestone, 0 comments for weeks). "Open" is not "come implement me"; don't sink effort there.

## Verifying an issue is actually unclaimed

In a repo this active, most visible P2 bugs already have a fix PR in flight. Before recommending an issue, check for an existing PR:

- Read the issue body for a self-link: "Implemented by PR #…" or "Superseded by #…". Reporters often leave it; it instantly disqualifies the issue.
- Check the issue timeline for cross-referenced PRs — this does NOT burn the (tiny) search quota: `GET /repos/NousResearch/hermes-agent/issues/{n}/timeline`, filter `event == "cross-referenced"` with `source.issue.pull_request` truthy.
- `gh search prs --repo NousResearch/hermes-agent --state all "<terms>"` — search open AND merged; an issue-only search misses already-fixed bugs.
- A PR closed with `merged=false` does not mean the bug is unpatched — it may have been superseded by a merged PR. Follow the "Superseded by #Y" chain to the merged PR before concluding the bug is still open.
- The GitHub REST search API rate-limits hard when unauthenticated (search ≈10/min vs core ≈60/hr). When search 429s, fall back to the timeline endpoint above.

## Finding a genuinely novel bug: mine the user's own operations

For a track record with zero competition, the strongest path is a bug the user hit themselves that upstream has not filed. Mine their running gateway/agent logs, then check novelty the same way:

- To tell live from stale: `errors.log` is the live file; `errors.log.1`/`.2` are rotated history. A high dedup count (`grep ERROR … | sort | uniq -c | sort -rn`) proves a live bug only if the hits are in the CURRENT file.
- A good first-issue shape: an append-only diagnostic log written with `open(path, "a")` and no size cap or rotation, that ballooned after a crash loop. Real disk impact, small localized fix (swap in a size-capped handler), rarely already reported. Confirm the writer by grepping the source for the log filename.
- Grep the log filename to find EVERY writer, not just the first one — a diagnostic log is often appended from multiple call sites (the CLI recorder AND the lifecycle ledger, for example). Fix all of them; a single-site fix leaves the sibling writer growing unbounded.
- The `%` trap: those log lines are pre-serialized JSON that routinely contain literal `%` (tracebacks, paths). Swapping in a stock `logging.Formatter` `%`-interpolates `record.msg` and corrupts or drops the line — emit `record.msg` verbatim via a raw-line formatter, or any `%` in a payload silently breaks the round-trip.
- If the fix routes a size-capped writer through a factory that can disable rotation on one platform (e.g. the Windows CLH fallback zeroes `max_bytes`/`backup_count` when portalocker can't take a lock), the cap silently vanishes and the original unbounded-growth bug survives there. Warn once via a one-shot module flag rather than letting the cap disappear silently — a trim is impossible on that path (multi-process renames hit WinError 32, which is precisely why the fallback exists).
- Rotation tests must assert a backend-agnostic invariant, not the exact cap: stdlib `RotatingFileHandler` rolls *before* the write that crosses `max_bytes`, `concurrent-log-handler` lets one more full record land first. Assert that a `.1` backup exists AND the live file stays `<= 2 * max_bytes` (or that `.1` predates the base file) — `<= max_bytes` alone passes on stdlib and fails on Windows CLH, which is the primary CI platform.
- External contributors cannot set labels/milestones/projects on another repo's issues/PRs: `gh issue edit --add-label` fails with a permission error and `--label` at create is silently ignored. Don't fight it — maintainer triage applies them. Labels appearing later mean a maintainer triaged, not that your create flags worked.

## Hard gates — a PR gets rejected if these are missed

- Python `requires-python` in `pyproject.toml` is `>=3.11,<3.15` (the PM dev env provisions 3.14, but the package metadata admits 3.11+); Node `^22.22.0` / `^24.11.0` / `>=26`.
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
