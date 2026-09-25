---
name: porting-skill-packs
description: "Port external skill/agent packs into Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, skills, import, port, claude-code, orchestrator, dedup, catalog]
    related_skills: [hermes-remote-backend, hermes-agent-skill-authoring]
---

# Porting external skill packs into Hermes

## When to use

- User has a `.agents/` directory (Claude Code) or another framework's skills/agents collection and wants it available in Hermes.
- User asks to "integrate these skills into the backend", "make this orchestrator work in Hermes", or "wire this pack up".

## Procedure

### 1. Locate the source

A `@folder:` reference to a Mac/local path fails with "path is outside the allowed workspace" and carries no file contents. Do not stall — check for a VPS mirror first: `/workspace/`, `/root/`, `/root/.hermes/attachments/`. State plainly which mirror you worked from and list which files.

### 2. Assess format compatibility

External packs are usually `<name>/SKILL.md` with `name:` + `description:` YAML frontmatter — the same minimum Hermes requires, so they load as-is. Before trusting them, grep for framework-specific tool refs to quantify adaptation cost:

```
grep -rl 'librarian\|$ARGUMENTS\|\.agents/\|\.claude\|AskUserQuestion' skills/
```

The cross-framework bits are almost always confined to a few files (the orchestrator plus a shared reference), not all N sub-skills — grep first, then decide whether bulk-editing is warranted.

### 3. Rewrite the orchestrator, don't mass-edit sub-skills

The orchestrator (e.g. `cmo.md`) is where the framework coupling lives. Fix it and leave the sub-skills as-is (they are mostly prompt templates the agent interprets on load). Keep the user's gate/checklist content verbatim; only replace the tool and path layer.

Convention mapping:

| Claude Code / other framework | Hermes |
|---|---|
| `.agents/skills/<name>` | `skill_view(name='<name>')` |
| "delegate to skill" | load via `skill_view` and follow; use `delegate_task` for parallel/independent heavy work |
| `question` tool | `clarify` |
| `librarian` (external info) | `web_search` / `web_extract` (+ `grounded-citations` for the citation ledger) |
| `explore` (internal docs) | `search_files` / `read_file` |
| `$ARGUMENTS` | the request/context passed when the skill is invoked |
| `.agents/` `.claude/` `memory/` `.local/research/` | project-relative paths under the working dir |

`librarian` and `explore` are framework TOOLS, not skills — map them, do not list them in the orchestrator's skill catalog as if they were skills.

### 4. Dedupe against bundled skills

An orchestrator's validation/gate machinery is often already shipped as a more mature bundled skill. Before reimplementing, check the bundle:

- business-plan feasibility/review gates → `business-plan-review` (ships a working `kpi_funnel_model.py` + `legal-risk-checklist.md`)
- fact/citation tracking → `grounded-citations`
- ongoing competitor monitoring → `competitor-news-monitor`

Delegate to bundled where it is better; keep the pack's skills where there is no equivalent. State this mapping in the orchestrator's "bundle との使い分け" section.

### 5. Verify catalog completeness mechanically (both directions)

Eyeballing misses dropped and ghost references. Verify BOTH ways:

```bash
# direction 1 — every real skill must appear in the orchestrator's catalog
for s in $(ls skills); do grep -q "\`$s\`" cmo/SKILL.md || echo "MISSING: $s"; done

# direction 2 — every name the catalog references must resolve to a real skill
# (or be a known tool / bundled skill)
grep -oE '`[a-z0-9-]+`' cmo/SKILL.md | tr -d '`' | sort -u | while read n; do
  [ -d "skills/$n" ] || echo "NOT A SKILL: $n";
done
```

Direction 2 also lists tools and bundled-skill names (e.g. `clarify`, `business-plan-review`) — those are legitimate. Only flag a name as a bug if it is meant to be a pack skill but has no directory.

### 6. Stage and install (remote VPS)

The sandbox skills tree is read-only. Stage the pack under `/workspace` (host-visible at `/home/hermes/.hermes/sandboxes/docker/default/workspace/`), then hand the user ONE fish-safe, semicolon-chained command to `cp -r` into `~/.hermes/skills/<category>/`. A new category (e.g. `marketing/`) avoids name collisions with bundled skills. See the `hermes-remote-backend` skill for the mount mapping.

## Pitfalls

- **`@folder:` to a Mac path fails silently** — a VPS mirror usually already exists; `ls` `/workspace`/`/root`/attachments before asking the user to re-upload.
- **Don't bulk-edit all sub-skills for convention drift.** Grep to find the few files that actually reference framework tools/paths; fix the orchestrator to establish canonical mappings instead.
- **A dropped or ghost catalog entry is invisible to eyeballing** — always run the two-direction reverse grep. Missing references are the #1 defect the user will ask about.
- **Reimplementing a gate a bundled skill already does better wastes the user's better tool.** Check `business-plan-review` / `grounded-citations` before writing the orchestrator's own gate text.
- **Fish shell has no heredoc** — give the user a one-line semicolon-chained `ssh` command, never a `<<'EOF'` block.
