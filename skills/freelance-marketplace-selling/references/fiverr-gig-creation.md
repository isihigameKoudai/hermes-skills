# Fiverr Gig Creation — wizard walkthrough

Observed step order in the current gig editor. Category and service type are **irreversible after publish**; everything else is editable later. Field caps: see `references/platforms.md`.

## Steps, in order

1. **Overview**
   - Gig title (80 chars, starts with "I will", no trailing period — see SKILL.md pitfalls).
   - Category → Subcategory.
   - **Search tags** — up to 5, letters/numbers.
   - **Positive keywords** — a *separate* field from search tags: the buyer search phrases you want to rank for. Relevant terms only (5–8); stuffing unrelated popular words reads as spam. Tags are product labels, positive keywords are buyer phrasings — don't duplicate them wholesale.

2. **Service type** — pick the one matching the offer (e.g. `CODE REVIEW`; the dropdown also offers `SOFTWARE TESTING`, `DESIGN REVIEW`, and a "Recommended" badge may appear). Then **Gig metadata**: a platform radio (Website testing / Mobile testing / Software testing / Database testing / Other) — pick the closest to the deliverable (a Next.js web-app review → Website testing).

3. **Expertise** — "Select the types & techniques that you focus on", **max 5**. For a code-review gig the fitting five are: **Clean Code, Code efficiency, Error handling, Design patterns, Version control**. (Other options: Algorithmic, Data structure, Unit tests, Other.)

4. **Scope & Pricing (Packages)** — three columns BASIC / STANDARD / PREMIUM. Per column: package name, package details, delivery time (days), feature checkboxes (Review report / Annotated screen shots / Session recording), price. The editor may also render live-session rows (Session length, Number of sessions) even for an async service — set them to the minimum. **Fill the BASIC column first**; the other two only resolve once it is set. Tick "Review report" for all tiers; leave "Session recording" unticked for an async service.

5. **Add extra services** — leave every session-based extra unticked (Extra minutes, Additional session, Session recording); they imply live calls. "Extra fast delivery" is the only sensible optional upsell.

6. **Description** — 1200-char cap, rich-text editor. Paste plain text, then apply the toolbar (bold, bullets) — pasted markdown renders literally.

7. **Requirements** — the Fiverr-default questions are optional; add custom ones (read-only repo access or scanner output; which tool they built with; optional focus area).

8. **Gallery** — images + optional video (see below).

9. Publish.

## Gig images (Gallery)

- Spec: **1280×769 px**, JPG/PNG. Up to **3 images, at least 1 required**. Video optional, **<75 s / <50 MB**.
- The **first image is the search thumbnail** — its headline must survive ~25% scaling. Big bold text, maximum contrast, one message per image.
- Show the **deliverable**, not stock imagery: a mock report / annotated finding list proves what the buyer receives (e.g. severity-badged rows with `file:line`).
- Suggested 3-image set for a review service: (1) headline + deliverable mock, (2) a "what I check" list, (3) the package prices.
- **Generate with PIL (Pillow)** — an AI image model garbles text and cannot be trusted for on-image copy. A headless browser is not required; DejaVu / Liberation fonts ship with most distros. Starter layout: `templates/gig_image.py`.
- **Verify before delivering**: load the rendered PNG back and check for overflow / overlap / clipping (e.g. via `vision_analyze`), and compute the right edge of any chip/row block against the neighbouring column's left edge.
