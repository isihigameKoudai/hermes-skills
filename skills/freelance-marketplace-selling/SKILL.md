---
name: freelance-marketplace-selling
description: Use when selling dev services on freelance marketplaces.
---

# Freelance Marketplace Selling

Selling a solo/dev service internationally (Contra, Upwork, Fiverr). Per-platform fee/payout facts live in `references/platforms.md` and MUST be re-verified at signup time because they drift.

## When to Use

- Choosing or ranking distribution channels for a solo service business.
- Writing profile/listing/gig copy for Contra, Upwork, or Fiverr.
- Building a Fiverr gig end-to-end — wizard step order, package pricing, and gig images. Field-by-field walkthrough: `references/fiverr-gig-creation.md`.
- Setting up payouts, tax forms (W-8BEN), or deciding a price ladder across marketplaces.

## Validation order (always)

1. **Validate demand before building the offer.** Post a free offer in the target community and/or list a minimal version on a marketplace first. Inbound signal is the market; a platform's existence is not.
2. **Platform ≠ market.** A niche's buyers live in specific communities (e.g. vibe-coders in r/vibecoding and X), not on general marketplaces. General marketplaces reach a different, broader buyer and test the wrong demand.

## Channel verification (the pivot rule)

- Before recommending or time-investing in a marketplace, load its **live site** and read the **current demand side** — featured roles, "trending", verified sellers, the hero copy. Not just fees/commissions.
- Marketplaces pivot. Contra repositioned from "commission-free freelancer platform" to "network for creative intelligence"; its homepage and featured roles are now design/UGC/motion/video, with dev roles relegated to the footer. Fee structure alone would have kept it ranked as a primary channel.
- If the buyer is not visible on the platform's homepage, downgrade the channel to "list it, don't invest time in it."

## Community posting safety

- Read a community's CURRENT self-promotion rules before drafting any post — they tighten faster than platforms pivot. Common traps: mod-approval gates for tools/services, "no shilling", and "no pessimism about the practice" clauses that permaban negativity toward how the audience works.
- Fear-framing the customer's own practice is a ban risk. If the service fixes problems caused by how the buyer works (e.g. AI-generated code shipping vulnerabilities), a pitch leading with "your code is 45% broken" reads as gatekeeping/pessimism and gets removed or permabanned. Lead with empowering, educational framing ("here's how to check your own app") and put the hard offer on a channel without such rules (X).
- When rules are strict or unclear, answer existing demand threads helpfully instead of posting a promo — it is the higher-leverage move and does not trip the rules.

## Positioning an async/no-call service

- Turn constraints into the pitch. Frame no-call and no-production-access as benefits to the client ("No calls. Just Pull Requests."), not as limitations.
- Never write "security audit" or "penetration test" — write "codebase review"/"codebase audit". The former are regulated terms that inflate expectations and liability.
- Use only verified stats with sources; never fabricate testimonials or numbers.
- Customer-facing artifacts (posts, profiles, LP) are written in English; internal planning and discussion in Japanese.
- Name the buyer's real tools in copy and in "which tool did you build with?" requirement options. For AI-generated (vibe-coded) apps the non-developer ICP overwhelmingly uses **Lovable, Bolt, Replit, v0, Base44**; **Cursor** is a developer-oriented editor and is the outlier. ~63% of vibe-coding users are non-developers (Vercel State of Vibe Coding 2025) and Replit reports 75% of its customers never write code — a tool list led by Cursor misreads the audience and narrows inbound.

## Payment & tax

- US marketplaces require a W-8BEN (individual) or W-8BEN-E (entity) plus the seller's country TIN (Japan: My Number). Japan has a US tax treaty, so claim reduced/exempt withholding. Upwork additionally requires a Statement of Source (work performed outside the US); missing forms trigger up to 30% withholding and blocked withdrawals.
- Platform minimums reshape the offer: a sub-minimum tier (e.g. a $199 lead magnet under Contra's $250 flat floor) cannot be listed there — route it to another channel or bundle it up. Check minimums before designing the price ladder.

## Pitfalls

- Do not assert comparative channel-demand claims ("buyers live in X, not Y") as fact without directly verifying — search real posts and read the live feed. If unverified, label it inference and say so; the correction is more expensive than the check.
- Account creation, identity verification, and posting under the user's own identity are **not delegable to subagents** — they require the user's legal identity. Subagents can produce artifacts (profile copy, posts, reports), not open accounts.
- When the user asks for "execution," split it explicitly into (a) artifacts you can build now, (b) things that need a credential/token you must request, and (c) things only the user can do. Say which bucket each task is in before delegating.
- Marketplace text fields (Fiverr especially) reject non-ASCII punctuation and enforce per-field character caps. Write copy to the limits up front and confirm the character count with a tool before handing the user copy. Exact caps per field live in `references/platforms.md`.
- Fiverr field strictness differs. **Profile tagline** ("Add title") accepts letters, numbers, spaces, and basic punctuation — `-` and `|` are fine, `·` (U+00B7) is not. The **gig title** must start with "I will" and must not end in a period — a trailing `.` alone fires `Title can contain letters and numbers only`. Do NOT blame hyphens for that error: deleting a hyphen did not clear it, deleting the trailing period did. Don't reword a working title around a punctuation mark you have not actually confirmed is the trigger.
- **Have the user type Fiverr title fields by hand, never paste.** Pasting carries invisible characters (e.g. a non-breaking space) that re-trigger `Title can contain letters and numbers only` even when the visible text looks clean; typing it clears the error.
- Fiverr locks the gig **category / service type after publish** — confirm the full path (e.g. Programming & Tech → QA & Review → Code Review) before publishing. The gig package editor may also show live-session fields (Session length / Number of sessions / Session recording) even for an async service; set them to the minimum and state "100% async, no calls" in the package description.
- Fiverr gig **images**: 1280×769 px, up to 3 (≥1 required); the first image doubles as the search thumbnail, so the headline must stay legible at ~25% scale. Generate them with PIL, never an AI image model — diffusion models garble text. Recipe: `references/fiverr-gig-creation.md`; starter script: `templates/gig_image.py`.
