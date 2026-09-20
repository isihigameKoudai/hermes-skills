# Article skeleton: infrastructure setup / troubleshooting write-up

Copy and fill. Section numbers are a suggestion — drop sections the source doesn't cover,
never invent content to fill one.

Language: match the user's. Headings, tables, and callouts in their language; commands,
error strings, and config keys verbatim.

---

```markdown
# <Outcome-shaped title>（実録・全エラー付き）

> 構成：**<client side> → <transport> → <server side>**
> 前提バージョン：<product> vX.Y.Z（<date> 時点）

## 0. なぜこの構成にしたのか

<The problem with the naive setup. Why the chosen architecture solves it.
Quote the official docs' own framing if it's good.>

```
<ASCII architecture diagram — clients on the left, transport arrows, server on the right>
```

## 1. <Foundation step: provision / install prerequisites>

<Requirements table: use case → recommended spec.>

### 💥 エラー①：`<verbatim error string>`

<What it actually means, as distinct from what it looks like.>

**対処：** <the fix>

<Any judgment call made here, and the reasoning — including the option that was
rejected and why.>

### 💥 エラー②：`<verbatim error string>`

<...repeat per error...>

## 2. <Install the main software>

<Install commands in a fenced block. Verification command right after.>

### 選択①：<a setup wizard choice that was non-obvious>

<Quote the actual prompt text from the log. Explain what the question is really asking —
setup prompts are frequently misread. Table of options → meaning → recommendation.>

> ⚠️ <Warning about anything the source got wrong here, forward-referencing §N.>

### 選択②：<next choice>

## 3. <Connect the model provider / external service>

<Table of plans, quotas, pricing — verified against the vendor page, with an "as of <date>".>

## 4. <Persistence / daemonization> — ここが最大の落とし穴だった

<Error-driven narrative. Include the commands that did NOT work and say so explicitly.>

| 選択肢 | 挙動 | 適する状況 |
|---|---|---|
| ... | ... | ... |

## 5. <Client-side connection>

<Modes table: which mode does what, which one is correct here, why the default is wrong.>

### 💥 エラー⑩：<the hardest one>

<Full log excerpt. What was tried and failed, as a bulleted list. The actual resolution.>

> ⚠️ **【重要・現行版では手順が変わっています】**
> <what changed> **現在の正規手順は §6 を参照。**

## 6. 現行版での正しい構成（推奨手順）

<The clean, verified, copy-pasteable procedure. This is what a new reader follows.
Server side, then client side, then per-additional-client.>

## 7. 日常運用

| 入口 | 方法 |
|---|---|

<Start/stop/restart commands. Troubleshooting quick-reference table:
症状 → 原因 → 対処.>

## 8. 検証で判明した誤情報・現行版との差分

**今回の作業ログには、現行の公式ドキュメントと食い違う記述が含まれていました。**

### ❌ 1. <claim>
### ❌ 2. <claim>
### ⚠️ 6. <claim>
### ℹ️ 11. <claim>

<Per the corrections format in references/verification-tactics.md.>

## まとめ：フェーズ別の課題と解決

| # | 課題 | 解決策 |
|---|---|---|

<2–3 one-line takeaways. Make them transferable lessons, not restatements.>

---

### 補足：秘匿情報のマスクについて

本記事では以下を伏せています。実際に構築する際はご自身の値に読み替えてください。

- <kind> → `[PLACEHOLDER]`

<If the raw source contained live secrets, say so and recommend against publishing
them verbatim.>
```
