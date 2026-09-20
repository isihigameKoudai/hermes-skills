# Reading skill change history (curator audit trail)

How to answer "what did past sessions change in my skills", and how much of it is actually recoverable. In this split-brain setup the skills tree is synced into the sandbox, so the curator state files are readable from inside the terminal backend at `/root/.hermes/skills/` (host: `/home/hermes/.hermes/sandboxes/docker/default/home/.hermes/skills/`, a copy of the agent's real `/home/hermes/.hermes/skills/` — the ledger entries reference the HOST paths, so don't be thrown by the mismatch).

## The three sources, in read order

1. **`.curator_ledger.jsonl`** — append-only per-mutation log. Each line: `actor` (`agent`/`curator`/`user`), `action` (`create`/`patch`/`archive`/…), `skill`, `evidence.session_id`, and `before`/`after` per-file `{path, sha256}`. This is the only place that records *who changed what, when*.
2. **`.usage.json`** — per-skill aggregate telemetry: `patch_count`, `use_count`, `view_count`, `created_at`, `last_patched_at`, `last_used_at`, `state`, `pinned`, and `created_by`. Aggregate only — says *how many times* and *when last*, never *what*.
3. **`.curator_backups/<utc-iso>/skills.tar.gz`** — full-tree snapshots taken before each curator run, with a `manifest.json` (`reason`, `skill_files` count). Diff successive snapshots to reconstruct what changed between runs.

`skill_manage`/CLI equivalents: `hermes curator ledger`, `hermes curator status`, `hermes curator rollback --list`.

## Pitfalls

- **The ledger does not backfill.** It is append-only but only began recording once the feature shipped. `usage.json` can show `patch_count: 8` on a skill while the ledger has zero entries for it. Treat the ledger as *recent changes only*; reconstruct older history by diffing `.curator_backups/` snapshots or reading session transcripts, never by assuming the ledger is complete.
- **The content-addressed blob store may be absent.** Single-edit rollback (`hermes curator rollback <entry-id>`) depends on `~/.hermes/.curator_backups/blobs/`. The ledger still records `before`/`after` sha256 even when the blobs were never materialized — so a non-empty ledger does NOT imply single-edit rollback works. Confirm the blobs dir exists before promising that rollback form.
- **`created_by` is the curator's jurisdiction switch.** Only `agent` skills are curator-managed (auto-archived/consolidated). `null` = bundled/hub/user-written (hands off), `learn` = created by a foreground agent at the user's request (also hands off). Use `.usage.json` `created_by` to tell which skills the curator will actually touch.
- **`state` drifts to `stale` on 14 days of non-use** (not an error). A skill whose `patch_count` you're auditing may sit in `stale`/`active`; that is lifecycle, not a sign of corruption.

## If rewindable line-level history is needed: git

The built-in history is coarse — it records *who/when/what-skill* and aggregate counts, never *the content of each edit*. The ledger stores `before`/`after` sha256s without materializing blobs, it does not backfill pre-feature edits, and snapshots are weekly, so intra-week overwrites are unrecoverable. When the user wants to roll back a skill's actual content to an arbitrary point, `git init` the skills tree and auto-commit:

```bash
cd ~/.hermes/skills && git init
```

`.gitignore` (drop noisy/telemetry paths; keep `.curator_ledger.jsonl` — it is the change metadata itself):

```gitignore
.curator_backups/
.archive/
.hub/
__pycache__/
*.pyc
.usage.json
.usage.json.lock
```

Prefer a **cron auto-commit** over a plugin/shell `post_tool_call` hook: the background curator / self-improvement review fork writes skills from a separate AIAgent process that can bypass foreground hooks, so a per-mutation hook misses those edits while a periodic `git add -A && git commit` catches every writer:

```cron
*/5 * * * * cd "$HOME/.hermes/skills" && git add -A && git commit -m "auto $(date +%F\ %T)" 2>/dev/null
```

`git init` must run on the **host** (the agent's real tree at `~/.hermes/skills`), never inside the terminal sandbox, whose `/root/.hermes/skills` is only a synced copy.