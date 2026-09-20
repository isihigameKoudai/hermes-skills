---
name: technical-writeup-from-logs
description: "Turn raw logs/transcripts into a fact-checked article."
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [writing, blog, technical-article, fact-checking, verification, redaction, documentation]
    related_skills: [humanizer, youtube-content]
---

# Technical Write-up From Logs

Turn messy raw material — AI chat transcripts, terminal scrollback, troubleshooting
notes, half-finished setup guides — into a technical article someone else can follow.

**Trigger:** the user attaches one or more logs/notes and asks for a 技術記事 / blog post /
write-up / "make this into an article". Especially when they add constraints like
"don't lose any information", "mask secrets", or "verify against the official docs".

The three things that make this hard, and that this skill exists to enforce:

1. **Completeness** — every fact in the source must survive into the output.
2. **Redaction** — raw logs are full of IPs, tokens, member IDs, home paths.
3. **Truth** — AI-generated source logs are frequently WRONG. Publishing them unchecked
   launders misinformation. Verification is not optional polish; it is the deliverable.

## Workflow

### 1. Inventory the sources before writing a word

List what each attached file contributes. Typical mix:
- a **troubleshooting transcript** (chronological, full of dead ends) → becomes the narrative spine
- a **cleaned-up setup guide** (already structured) → becomes the "correct procedure" section
- a **conceptual/overview doc** → becomes the intro and the "why this architecture" section

Do NOT merge them into one flat chronology. Map each source to the section it feeds.

### 2. Load the governing skill / official docs FIRST, in parallel

Before drafting, fetch the authoritative reference for the subject matter in the
same turn as your first `skill_view`. Batch independent fetches — do not serialize.

For any product with a docs site, look for a machine-readable index first:
- `/<docs>/llms.txt` — curated page index with descriptions (small, cheap, load it)
- `/<docs>/llms-full.txt` — every page concatenated (can be MBs; only if you need breadth)

That index tells you exactly which pages to pull, instead of guessing URL slugs and
collecting 404s.

### 3. Draft the spine: chronological failures, each with root cause

The most valuable structure for a setup/troubleshooting article is:

```
💥 Error N: <verbatim error string>
  → what it actually means (not what it looks like)
  → why it happened here
  → the fix (exact command)
  → what was tried and did NOT work  ← keep these, they have real value
```

Verbatim error strings are what people paste into search engines. Preserve them exactly.
Failed attempts are signal, not noise — record them explicitly as "tried and did not work"
so a reader with the same symptom stops going down that path.

### 4. Mask secrets with a legend, not silently

Replace with descriptive placeholders, and add a closing section listing what was masked
so the reader knows to substitute their own values:

| Kind | Placeholder |
|---|---|
| Public IP / hostname | `[VPSのIP]` / `[HOST]` |
| API / bot tokens | `[xoxb-...]`, `[xapp-...]`, `***` |
| User / channel / member IDs | `[MEMBER_ID]`, `[CHANNEL_ID]` |
| Passwords, session tokens, signing secrets | `[STRONG_PASSWORD]`, `[SESSION_TOKEN]` |
| Local home paths | generalize `/Users/<realname>/…` → `~/…` |

Also flag it in the reply: if the attached raw logs contained live secrets, say so and
recommend not publishing them verbatim.

### 5. Verify EVERY concrete claim — then publish the diff

This is the step that gets skipped and the step that matters most. Check at minimum:
- command names and subcommands (real ones, not invented ones)
- service / unit names (guessing these is a top source of wasted user time)
- config file names, formats, and key paths (`config.yaml` vs `config.json`)
- env var names — especially ones that may have been **deprecated or removed**
- flags whose behavior changed (a flag that became a no-op is a silent trap)
- pricing, tier, quota, and count claims ("40+ skills", "$20/mo") — these rot fast
- security explanations — a feature described only by its side effects is misinformation

Then **write a dedicated section that lists the corrections**, categorized:
`❌ wrong / no longer valid` · `⚠️ inaccurate or incomplete` · `ℹ️ minor / superseded`

Give each one: what the source said → what is actually true → the citation. Keep the
original (wrong) attempt in the narrative body, but attach an inline warning callout
pointing forward to the corrections section. Readers deserve both the lived experience
and the correct answer.

See `references/verification-tactics.md` for the concrete fetch tactics, the
claim-type checklist, and the corrections-section format.

See `references/hermes-agent-remote-dashboard.md` for a verified knowledge bank on
Hermes Agent's dashboard / Desktop remote connection (auth providers, systemd units,
deprecated env vars, Slack setup) — useful when the source logs are about installing
or connecting to a remote Hermes Agent instance.

### 6. Assemble

Start from `templates/article-skeleton.md` — a section-by-section scaffold for
infrastructure setup / troubleshooting write-ups. Delete sections the source doesn't
cover; never invent content to fill one.

## Style rules for this class of task

- **Match the user's language.** If they wrote in Japanese, the article is in Japanese —
  including headings, tables, and callouts. Code, commands, and error strings stay verbatim
  in their original language.
- **Lead the reply with the verification verdict**, not with pleasantries. "I checked the
  attached files against the official docs; 5 items are wrong" is the first sentence.
- Tables for anything enumerable (options, scopes, plans, error→cause→fix).
- Fenced code blocks for every command. Never inline a multi-word shell command in prose.
- Callouts (`>` blockquote with ⚠️ / 💡 / 📌) for warnings and version caveats.
- Close with a summary table mapping phase → problem → solution, and 2–3 one-line takeaways.
- Do not pad with generic advice the source didn't contain. Completeness means "nothing lost",
  not "nothing added is fine".

## Pitfalls

- **Don't trust an AI-authored source doc.** If the user says "this guide was generated by
  an AI", treat every command in it as unverified. The most expensive failure mode in this
  session's source material was a deprecated env var that sent the user down a dead end.
- **Don't silently correct.** Rewriting the source to be right, without flagging it, robs
  the user of the ability to trust or audit the article. Correct AND disclose.
- **Don't drop the dead ends.** "Here's the clean happy path" articles are worthless for
  the person currently staring at the error.
- **Don't guess a service/unit/binary name to fill a gap.** If the source used a name and
  you can't confirm it in the docs, that's a finding for the corrections section.
- **Don't assume a documented workaround is still needed.** Flags and env vars get removed
  once the underlying behavior becomes the default. Check current docs before repeating one.
- **Ask before file-writing the article** if the environment's write path is unclear —
  deliver as chat markdown first, offer the file as a follow-up.
- **If the user then asks for a file and the write backend is unavailable** (Docker backend
  down, `execute_code` / `write_file` / `terminal` all fail with a backend error), do NOT
  keep retrying or claim the tools are broken — that hardens into a refusal. Use `clarify`
  to offer three paths: wait for backend recovery and retry, user copies the chat markdown
  into a `.md` file themselves (instant), or user pastes to a Gist/external host. The
  article is already delivered in the chat — the file is a convenience, not the deliverable.
- **`MEDIA:` delivery failing with "missing, unreadable, or too large" even though
  `execute_code` / `write_file` succeeded** means the file landed in a container-internal
  path the host-side Hermes process cannot see. When the terminal backend is `docker`,
  `execute_code` runs inside a container; `/root/` and `/tmp/...` there are NOT the host's.
  The host-shared write target is `/workspace/` (mounted rw from the host, owned by the
  host user, typically uid 1000). Write there and `os.chown(path, 1000, 1000)` so the host
  user can read it, then re-issue the `MEDIA:` link with the `/workspace/...` path. Do not
  assume the first write path was wrong because the backend is broken — the backend was
  fine, the path was just not host-visible. `~/.hermes/cache/{documents,images,...}` and
  `~/.hermes/skills` are mounted **read-only** from the host, so they are not write targets.

  **Host-side path resolution when `MEDIA:` still fails after writing to `/workspace/`.**
  Read `/proc/self/mountinfo` from inside the container — the `workspace` mount line
  reveals the host-side source subdirectory. As of 2026-08 the mapping is:
  - container `/workspace` → host `~/.hermes/sandboxes/docker/default/workspace/`
  - container `/root` → host `~/.hermes/sandboxes/docker/default/home/`
  So a file written to `/workspace/article.md` in the container is visible at
  `~/.hermes/sandboxes/docker/default/workspace/article.md` on the VPS. Tell the user
  that exact path so they can `scp` it from the Mac — do NOT just say "look around
  ~/.hermes/". A `find / -name <filename>` from the host also works but is slower and
  needs `sudo` plus a password prompt.

  **`scp` must run from the Mac, not from inside the VPS.** If the user is logged into
  the VPS over `ssh`, an `scp xserver:...` command issued there will fail with
  `Could not resolve hostname xserver: Temporary failure in name resolution` — the
  `xserver` alias lives in the Mac's `~/.ssh/config`, not the VPS's. Instruct the user
  to `exit` back to the Mac first, then run `scp xserver:~/.hermes/sandboxes/docker/default/workspace/<file> ~/Desktop/`.
