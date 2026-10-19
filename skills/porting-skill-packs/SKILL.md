---
name: porting-skill-packs
description: "Port external skill/agent packs into Hermes."
version: 1.2.0
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

### 3b. Single-skill packs (one skill dir + `scripts/` + `references/`)

Many packs are not orchestrators at all — one `<name>/SKILL.md` plus `scripts/*.py`, `references/*.md`, `examples/`. The adaptation is the tool/path layer only:

- Add a short "Hermes での動かし方" section with the mapping: subagent-role prompts → `delegate_task` (put "do not summarize, do not write files" in the child's `context` — children default to summarizing), web search/fetch → `web_search` / `web_extract`, slash commands → the spoken trigger phrases, `~/<dir>/` → sandbox `$HOME` plus the host-visible path.
- State ONCE, in the tools section, that `scripts/...` means the skill's own directory (`skill_dir` from `skill_view`), and call them by absolute path. Installed skills are not cwd, so bare relative paths silently miss.
- Copy any auxiliary directory the SKILL.md cites by repo path (`examples/demo`, fixtures, sample sources) into the skill dir and rewrite the citation to be skill-relative — otherwise the reference dangles after install and the demo can't be run.
- Add a "同梱スキルとの使い分け" section naming the bundled skills that overlap, so a future agent picks the better tool instead of the ported one.

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

### 5b. Smoke-test the staged copy before handing over the installer

A green unit-test suite does not prove the CLI paths work — run the pack's own tests AND one real invocation of every script, in a throwaway dir, from the absolute skill path:

```bash
python3 -m pytest -q                       # pip install pytest pyyaml if absent
python3 <skill_dir>/scripts/report.py <skill_dir>/examples/demo   # bundled fixture
# then one real call per remaining script (fetch a real URL, hit the real API, read a real feed)
```

Fix breakage in the STAGED copy and fold every fix into the mapped SKILL.md as a rule (e.g. "`file` is the bare filename under `sources/`, not `sources/<file>`"), not just into your head. Report per-script results — the user wants evidence the port was exercised, not a claim that it was.

### 5c. Prove fidelity with hashes (the user will ask)

A port is judged on whether the pack's code was copied or retyped. Make the answer mechanical:

```bash
git clone --depth 1 <repo> /workspace/<repo>          # never hand-copy code below SKILL.md
cp -r /workspace/<repo>/<path-to-skill> <staged>/
scripts/verify-port-fidelity.sh /workspace/<repo>/<path-to-skill> <staged>/<name>
```

Report three things: the upstream commit (`git log -1 --format='%H %ad %s' --date=iso`), which files are byte-identical, and — for the SKILL.md you edited — added-line count plus the replaced lines, so the user can see no original content was dropped. `scripts/verify-port-fidelity.sh` prints exactly that table; pass the file you intentionally edited as `--expect-diff SKILL.md` so it is reported as expected rather than as a defect.

Run it before answering any "did you just paste it?" question, and quote the hashes rather than asserting good faith.

### 6. Stage and install (remote VPS)

The sandbox skills tree is read-only. Stage the pack under `/workspace` (host-visible at `/home/hermes/.hermes/sandboxes/docker/default/workspace/`), then hand the user ONE fish-safe, semicolon-chained command to `cp -r` into `~/.hermes/skills/<category>/`. A new category (e.g. `marketing/`) avoids name collisions with bundled skills. See the `hermes-remote-backend` skill for the mount mapping.

### 7. Keep ported packs out of any auto-publish path

When the host auto-syncs `~/.hermes/skills` to a shared GitHub tap (this setup: `~/.hermes/scripts/sync-skills-to-tap.sh` on a no-agent cron), a ported third-party skill becomes public the moment it is installed. Unless the user asks for it to be published, exclude it:

1. Add the name to the sync script's `EXCLUDE` set. That filters at copy time, so nothing is ever staged — stronger than a `.gitignore`, which only hides files from `git add` while the working tree still holds them.
2. Prove the exclusion without pushing: run the script with a throwaway `HOME` and `HERMES_HOME` whose `.usage.json` marks the ported skill `created_by: agent` (the condition that makes it eligible), then check the tap's `skills/` and `README.md` contain every other skill and not that name.
3. Stage the patched script and give ONE fish-safe semicolon-chained command that copies script + skill together and ends by grepping the `EXCLUDE` line, so the user sees it landed.

Also state plainly what is already public (query the repo tree) before promising anything — "nothing has been pushed" is only credible with the tree listing.

## Pitfalls

- **A clean framework grep means the port is a COPY job, not a rewrite.** When the pack already carries its own fallback ("if you have no subagents, search it yourself"), do not invent adapters — add the mapping table, the script-path rule, and the overlap section, and leave the body verbatim. Info loss is the defect the user will notice.
- **Anything cited as `repo/...` breaks after install.** Fixtures, `examples/`, and cross-directory references must be copied into the skill dir and rewritten skill-relative in the same pass.
- **Bundled scripts are called by absolute path from `skill_dir` only.** A relative `scripts/x.py` works only while cwd is the skill dir, which never happens for an installed skill.
- **Never retype a pack's code.** Clone, `cp -r`, then show sha256 matches against the clone. "I rewrote it carefully" is unverifiable and reads as a defect to this user; hashes plus the upstream commit are the only answer that holds.
- **Check the path exists before calling a hash mismatch a difference.** A fixture can live at the repo root rather than under `skills/<name>/`; comparing the wrong path made `sha256sum` print "No such file" and the report claim a diff that did not exist. Compare against the clone's real layout.
- **An auto-publish cron turns "install" into "publish".** Check for a tap sync script before copying a ported skill into the host skills tree, and prove the `EXCLUDE` entry with a fake-`HOME` run instead of trusting the edit.
- **A port's auxiliary assets need a home in the skill dir** before the install command goes out (`examples/`, fixtures); copying them afterwards means a second round-trip with the user.
- **`@folder:` to a Mac path fails silently** — a VPS mirror usually already exists; `ls` `/workspace`/`/root`/attachments before asking the user to re-upload.
- **Don't bulk-edit all sub-skills for convention drift.** Grep to find the few files that actually reference framework tools/paths; fix the orchestrator to establish canonical mappings instead.
- **A dropped or ghost catalog entry is invisible to eyeballing** — always run the two-direction reverse grep. Missing references are the #1 defect the user will ask about.
- **Reimplementing a gate a bundled skill already does better wastes the user's better tool.** Check `business-plan-review` / `grounded-citations` before writing the orchestrator's own gate text.
- **Fish shell has no heredoc** — give the user a one-line semicolon-chained `ssh` command, never a `<<'EOF'` block.
