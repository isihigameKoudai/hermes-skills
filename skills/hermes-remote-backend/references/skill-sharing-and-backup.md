# Skill backup & team sharing (git autocommit + custom tap)

Proven setup for this VPS backend: (1) keep the live skills tree under git for history, and (2) auto-publish agent-learned skills to a GitHub tap with secret masking. Both run as `no_agent` cron jobs (zero LLM/credit).

## 1. Local git history for ~/.hermes/skills/

- `git init` the HOST skills dir (`/home/hermes/.hermes/skills/`) — done on the host, not the sandbox (skills is `ro` in the sandbox).
- `.gitignore`: `.curator_backups/`, `.archive/`, `.hub/`, `__pycache__/`, `*.pyc`, `.usage.json`, `.usage.json.lock`. Keep `.curator_ledger.jsonl` tracked (it's the change log).
- Auto-commit via a `no_agent` cron job: `git add -A`; commit only when `git diff --cached` is non-empty; `exit 0` when nothing changed (silent tick). Schedule `*/5 * * * *`.

## 2. Team sharing via a custom GitHub tap

A tap is any GitHub repo laid out as `skills/<slug>/SKILL.md` (flat — each skill dir directly under `skills/`). Members subscribe with:

```bash
hermes skills tap add OWNER/repo
hermes skills install OWNER/repo/<slug>
```

Key gotcha: the LIVE skills tree is category-hierarchical (`creative/foo/SKILL.md`), NOT tap-flat. So you can't point a tap at `~/.hermes/skills/` directly — a sync script must flatten it.

### Sync script (with secret masking)

`~/.hermes/scripts/sync-skills-to-tap.sh` — runs on the host, driven by a second `no_agent` cron job (`*/10 * * * *`). Logic:

1. Read `~/.hermes/skills/.usage.json`; select skills where `created_by == "agent"` (plus a manual `EXTRA` list, minus an `EXCLUDE` set).
2. For each skill: find its dir (recursive, basename matching a `SKILL.md`), then copy to `~/hermes-skills-tap/skills/<name>/`, flattening the category level.
3. **Secret masking before copy** — regex-replace, then write masked text:
   - public IPv4 (skip loopback/private/link-local/multicast) → `[REDACTED_IP]`
   - email → `[REDACTED_EMAIL]`
   - API keys (`sk-…`, `sk-ant-…`, `ghp_…`, `xoxb-…`, `AKIA…`, `AIza…`) → `[REDACTED]`
   - `-----BEGIN … PRIVATE KEY-----` → `-----BEGIN REDACTED KEY-----`
   - binary files copied as-is; `__pycache__`/`*.pyc`/`.git` skipped.
   - Log mask counts to `.sync.log` (gitignored).
4. `git add -A`; commit + `git push origin main` only when there's a diff; `exit 0` otherwise (silent).

Bundled skills (~83) are NOT synced — recipients already have them via `hermes update`, and re-publishing duplicates/churns. Sync only agent-learned + manual skills.

### Host setup (one-time, done over SSH from the user's Mac)

1. SSH key on the host + add pubkey to GitHub (https://github.com/settings/keys). First `ssh -T [REDACTED_EMAIL]` from the host needs `ssh-keyscan github.com >> ~/.ssh/known_hosts` to avoid "Host key verification failed".
2. `git clone [REDACTED_EMAIL]:OWNER/repo.git ~/hermes-skills-tap`, set `user.name`/`user.email` to GitHub-linked values, place a README.
3. Place `sync-skills-to-tap.sh` under `~/.hermes/scripts/` (copy from the sandbox's `/workspace/` over SSH).
4. Create the `no_agent` cron job pointing at the script.

## Pitfalls

- **User's Mac shell is fish** — heredocs (`<<'EOF'`) are invalid. Give `ssh host 'a; b; c'` one-line semicolon form.
- **cron script-existence check**: `cronjob(action=create, script=...)` fails with "Script file not found: /home/hermes/.hermes/scripts/..." until the file exists on the HOST. Place it first, then create the job.
- **public vs private tap**: public = no auth for members' `tap add`; private = each member needs GitHub auth. No live secrets in the shipped skills, so public is safe, but environment-specific know-how may still argue for private.
- **Skills copied into `~/.hermes/skills/` by hand (`cp`/`scp`, not via `skill_manage`) never carry the `created_by == "agent"` mark**, so the tap sync silently skips them — they have no `.usage.json` entry, or a `created_by: null` one. To publish a hand-copied skill (e.g. a ported Claude Code `.agents/skills/` pack, or anything the user `cp`'d into place), add its slug to the `EXTRA` list in `sync-skills-to-tap.sh`. Only skills the agent authors through `skill_manage` are auto-marked for sync; `EXTRA` is the manual escape hatch.