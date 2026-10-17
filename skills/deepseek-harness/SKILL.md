---
name: deepseek-harness
description: "Delegate coding to DeepSeek Harness (dsh) headless or SDK."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, DeepSeek, dsh, Autonomous, Refactoring, Orchestration]
    related_skills: [claude-code, codex, opencode, hermes-agent]
---

# DeepSeek Harness (dsh)

DeepSeek's open-source agent harness (MIT, "everything is a plugin" on Cordis). Same class as opencode / claude-code / codex — a terminal coding worker Hermes orchestrates, NOT a competitor to Hermes itself. Layers: model (DeepSeek V4.x) → coding-CLI worker (dsh / opencode / codex / claude-code) → personal orchestrator (Hermes).

## When to use

- User wants coding delegated to DeepSeek Harness specifically
- Cheapest frontier-adjacent coding worker (paired with DeepSeek V4.x; 1M context)

## Key fact: dsh is a harness, not just a web UI

The root README only shows `dsh web` (Web UI at `http://127.0.0.1:3080`), which misleads people into thinking dsh is interactive-only. Headless driving is first-class. The authoritative entry-point reference is `apps/cli/README.md` in the repo (or the docs site `https://deepseek-harness.github.io/deepseek-harness/`), not the root README.

## Entry modes (official CLI reference)

| Command | Purpose |
|---|---|
| `dsh --profile headless "task"` | One fresh persisted session, print final answer, exit — the `opencode run` / `codex exec` equivalent |
| `dsh --profile sdk` / `sdk-minimal` | Serve SDK clients over JSON-RPC stdio |
| `dsh --profile acp` | Serve automation clients over ACP stdio (the VS Code/Zed protocol) |
| `dsh web` | Web UI (human-facing) |
| `dsh --profile <name>` | Boot a named profile |

## Procedure

### Install

- npm: `npm i -g @deepseek-ai/dsh` (needs a Node runtime)
- Python SDK (prefer when Node version is uncertain): `pip install deepseek-harness-sdk` — bundles the `dsh` runtime + native sidecars, no system Node needed.

### Auth

`DEEPSEEK_API_KEY` env var (optional `DEEPSEEK_BASE_URL` for an OpenAI-compatible proxy). Profiles auto-init under `$DSH_HOME/profiles/<name>` on first use.

### One-shot (headless) — the `opencode run` analog

```
terminal(command="dsh --profile headless 'fix the failing tests'", workdir="/path/to/repo")
```

The invoking directory IS the default workspace root — set `workdir` to the target repo.

### Session-managed / multi-turn (Python SDK)

```python
from deepseek_harness import DeepSeekHarness
with DeepSeekHarness(provider="deepseek-official", model="deepseek-v4-flash",
                     cwd=str(workspace), dsh_home=str(home), profile="sdk-minimal") as h:
    r = h.run("Inspect the repo and fix the failing tests", session_id="ex-001")
print(r.final_response)
```

Reuse `session_id` to continue the same durable conversation across `run()` calls.

## Pitfalls

- `dsh --profile headless` runs a FRESH session per invocation. For multi-turn continuation use the Python SDK's `session_id` reuse; do not assume `--resume` works on the headless profile (it is documented for the tui profile, unverified for headless).
- Source build requires Node `^22.19 || >=24`. The prebuilt npm CLI's floor is lower and unverified on old Node (e.g. v20); if headless fails to launch on an old Node, switch to the Python SDK — it bundles its own runtime and sidesteps Node entirely.
- `sdk-minimal` ships only `bash` + `read_image` + `working_directory`; `str_replace_editor` is opt-in via a profile patch, and it pins `danger-full-access`. Run it against a disposable checkout, not a live repo. Full toolset lives in the standard `sdk` / `headless` profiles.
- Profiles live under `$DSH_HOME/profiles/<name>`, not the repo. The Python SDK never silently reads `~/.dsh` — pass `dsh_home` explicitly.

## Verification

Smoke test with `DEEPSEEK_API_KEY` set:

```
terminal(command="dsh --profile headless 'Respond with exactly: DSH_OK'")
```

Success: output contains `DSH_OK`, exit code 0.
