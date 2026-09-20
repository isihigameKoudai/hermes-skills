# Verification tactics for fact-checking a write-up

Concrete mechanics for step 5 of the parent skill. The goal is to confirm or refute
every concrete claim in the source material at low token cost.

## Fetch order (cheapest first)

1. **`web_extract` on the docs root** — orients you and often reveals the docs' own
   machine-readable index links.
2. **`<docs>/llms.txt`** — a curated index of every page with one-line descriptions.
   This is the single highest-value fetch: it hands you the exact page URLs so you stop
   guessing slugs. `<docs>/llms-full.txt` is the whole corpus concatenated — often MBs,
   only pull it when you need breadth over precision.
3. **`web_extract` on 2–5 specific pages, batched in one call.** Independent fetches go in
   the same assistant turn.
4. **`web_search` with a targeted phrase** when the docs are silent — issue trackers and
   changelogs are where you learn a flag was *removed*, which docs rarely announce.

## When `web_extract` truncates a huge reference page

Long reference pages (env var tables, CLI references) get head+tail truncated, and the
part you need is usually in the omitted middle. Two ways through:

**A. Browser + JS extraction (surgical, cheapest).** Navigate, then pull only the rows
you care about with a console expression:

```js
[...document.querySelectorAll('tr')]
  .filter(r => r.innerText.includes('PREFIX_'))
  .map(r => r.innerText.replace(/\n/g,' | ')).join('\n')
```

or slice around a heading:

```js
(() => { const t = document.body.innerText;
         const i = t.indexOf('Section Heading');
         return t.slice(i, i + 5000); })()
```

**B. Read the cached full text.** `web_extract` writes the complete page to disk and
prints the path plus a ready-made `read_file` call with an offset. Use it when the
filesystem tool is available.

## The claim checklist

Walk the draft and interrogate each of these — they are ordered by how often they turn
out to be wrong in AI-authored source docs:

| Claim type | Why it rots | How to confirm |
|---|---|---|
| Env var exists | Removed once behavior became default | Search the env-var reference for the exact name; absence = deprecated |
| Flag behavior | Silently becomes a no-op | Read the flag's row in the CLI reference; look for "deprecated / no-op" |
| Service / unit name | Guessed, never existed | Search docs for `install` / `systemd` / `launchd` sections |
| Config file name & format | `.json` vs `.yaml` confusion | Directory-structure section of the config docs |
| Config key path | Renamed across versions | The commented full-config example in the docs |
| Counts ("40+ skills") | Grows every release | The catalog/reference page that enumerates them |
| Pricing / tiers / quotas | Changes quarterly | The vendor's own pricing page, not a blog |
| Security feature purpose | Source described side effects only | The feature's dedicated docs page — read "What it is" AND "What it is not" |
| Required scopes / permissions | Incomplete lists cause "works in DM, not in channel" bugs | The platform integration page's full scope + event tables |

## Structuring the corrections section

Three severity buckets, most severe first. Each entry:

```
### ❌ N. <the claim, stated plainly>

<What the source said, and that it was followed.>

- <Citation 1 — a doc quote or commit message>
- <Citation 2>

<What the correct current procedure is, or a pointer to the section that has it.>
```

Severity meanings:
- **❌** — actively wrong now. Following it wastes time or breaks something.
- **⚠️** — incomplete or misleading. Works, but the reader will misunderstand the why.
- **ℹ️** — minor drift: superseded flag, changed count, better-recommended alternative.

Quote the docs verbatim for the load-bearing corrections. A paraphrase is just another
unverified claim.

## Cross-referencing the narrative

For every ❌ item that appears in the article body, insert a callout at the point of
first occurrence:

```
> ⚠️ **【重要・現行版では手順が変わっています】**
> <one-line statement of what changed>
> **現在の正規手順は「N. 現行版での正しい構成」を参照。**
```

This keeps the lived narrative honest without turning it into a trap.
