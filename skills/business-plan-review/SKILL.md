---
name: business-plan-review
description: "Review business plans: feasibility math, facts, risk."
version: 1.0.0
author: Nous Research
license: MIT
metadata:
  hermes:
    tags: [business-plan, strategy, review, feasibility, unit-economics, risk, gtm]
    category: research
    related_skills: [grounded-citations, xlsx, document-to-action-items]
---

# Business Plan / Strategy Document Review

Reviewing a business plan is NOT summarizing it or praising its insights. The
job is to find the places where the plan **cannot work** — and prove it with
arithmetic, primary sources, and law, before the user spends months executing.

A plan can have excellent market insight and still be unexecutable. Those are
independent axes. Grade them separately.

## When to Use

- User asks to review / critique / 徹底レビュー a business plan, strategy doc,
  GTM plan, pricing proposal, or new-venture report.
- User asks to "fix" or rewrite such a plan under new constraints.
- An agent (e.g. a self-authored CMO/strategy agent) produced a plan and the
  user wants it checked.

## Core Principle

> Most strategy documents are optimized to be **persuasive**, not **survivable**.
> Your value is the adversarial pass they never ran on themselves.

Narrative fluency (Mermaid diagrams, tiered matrices, "4 protocols") is cheap
and is NOT evidence of soundness. Treat polished structure as a reason for more
scrutiny, not less.

## The Four Gates

Run these in order. Each gate can kill or reshape the plan; running them out of
order wastes work.

### Gate 0 — Operator Constraints (BEFORE writing any review)

The single highest-leverage question set. Skipping it causes total rework:
a plan built on capabilities the operator does not have must be rewritten from
the offer definition up, not patched.

Ask (or extract from the doc; if absent, ASK — do not assume):

1. **Language** — read / write / speak, separately. "Cannot speak English"
   deletes every synchronous offer, sales call, and live-narration deliverable.
2. **Hours** — weekly capacity ceiling. This becomes the binding constraint in
   Gate 2.
3. **Timezone** — vs. target market; whether night work is acceptable. Drives
   SLA design (and can be turned into an "overnight delivery" advantage).
4. **Access/permissions** — may they touch client production, consoles,
   credentials? "No" changes the deliverable format itself.
5. **Capital** — initial spend, and months survivable at zero revenue. This is
   the basis for the exit criteria.
6. **Legal entity & insurance** — sole proprietor vs. company; insured or not.
7. **Existing assets** — testimonials, audience, portfolio, prior clients.
   Zero assets invalidates any month-1 revenue projection.
8. **What they refuse to do.** Most-missed question. Ask it explicitly.

Record the answers as **Chapter 0 of the revised plan**. Constraints are the
foundation, not a footnote.

### Gate 1 — Fact Verification (right after research)

Label every number, price, fee, product name, and statistic as one of:

| Label | Meaning | How to write it |
|---|---|---|
| `[verified]` | Confirmed against a primary source (official pricing/doc page) | State plainly; cite the URL |
| `[claimed]` | Self-reported by the party that benefits | "X's published figure is…" |
| `[estimated]` | Not verified; inference or hearsay | "estimated / requires verification" — **never** assert |

Always verify, every time:

- **Platform fees.** Before writing "zero fees / free," open the official
  pricing page. Zero *commission* and zero *cost* are different claims.
- **Product and model names are current.** AI-adjacent names go stale in
  months; a two-generation-old model name in a strategy doc destroys the
  reader's trust in everything else on the page.
- **Statistics** — source and year.
- **Regulated terms.** "Audit," "certification," "penetration test" carry
  compliance meaning. Misuse inflates both expectation and liability.

**Competitor analysis minimum bar.** A price-tier matrix (budget / mid /
premium) is market *structure*, not competitor analysis. Require:

- >=5 **direct** competitors by name, with real prices, offers, URLs
- >=3 of them **individual or small** operators (listing only big agencies is
  an evasion — the user's actual competition is other solos)
- "No competitors" is almost never true. It means the search was too narrow.

### Gate 2 — The Arithmetic Gate (highest-value, most-skipped)

**Any plan containing a revenue target must contain the funnel that produces
it.** Its absence is the single most common fatal defect. A plan without this
math is not optimistic — it is unfalsifiable.

Required, all of it:

```
A. Top-down funnel
   revenue target -> deals -> opportunities -> leads -> touches
   Every conversion rate stated AND labeled [measured]/[benchmark]/[assumed]

B. Bottom-up effort
   delivery hours + SALES hours + admin (~15%) = total hours
   ** Sales hours are the near-universal omission. **
   total / 4.33 = hours per week

C. Reconciliation
   weekly hours <= Gate 0 capacity ceiling?
   If NO: the plan is broken. Do not present it as achievable.
   Change assumptions and recompute. Then rank the levers by effect size.

D. Unit economics
   effective hourly = (price - payment fees) / (delivery + sales hours)
   Check it against the positioning the doc claims for itself.

E. Vocabulary
   "Profit margin" requires counting the operator's own labor, payment
   fees, and tax. Otherwise it is GROSS margin. A solo service business
   claiming "98% operating margin" has simply not costed its own time.
```

**Compute this in code, not in your head.** See
`references/feasibility-model.md` for the build-and-verify recipe and
`templates/kpi_funnel_model.py` for a working generator. Shipping an
interactive model beats asserting a number: the user can change assumptions
and re-derive the verdict themselves.

### Gate 3 — Legal & Risk Gate (before delivering)

Checklist in `references/legal-risk-checklist.md`. Never skip these three:

- **Any tactic involving unauthorized access to someone else's system** —
  scanning, probing, "find their vulnerability and DM them." This is a
  criminal-liability question (CFAA / UK CMA), not a marketing question.
  Redesign to consent-first (public call for applicants + written permission)
  and passive observation only.
- **"Prepaid, therefore zero risk" is false.** Chargebacks pierce a
  no-refund policy. Excess dispute rates threaten the payment account itself.
- **Missing contract chapter.** Liability cap, no-warranty (especially for
  security work), NDA, IP assignment, AI-tool disclosure.

Two artifacts are mandatory in the revised plan:

- **Risk register** — risk x likelihood x impact x mitigation
- **Exit criteria** — numeric and dated. "Reassess if it goes badly" is not a
  criterion. "Under 3 paid deals at day 90 -> switch channel from X to Y" is.

## Internal Consistency Pass

Cheap, and catches embarrassing defects:

- Does the doc meet the standards it defines for itself? (A plan positioning
  at "$75-150/hr" whose own offers compute to $48/hr contradicts itself.)
- Executive-summary numbers == body numbers?
- Diagrams == prose?
- Anything listed as a strength that a later chapter lists as a constraint?

Then: **write five objections to your own review.** Anything you cannot answer
is a hole in the review, not in the plan.

## Output Shape

Lead with a **graded scorecard by axis** (market insight / positioning / offer
/ factual accuracy / feasibility / risk management / validation plan). Split
grades are the honest result and the most useful signal — "insight A,
feasibility D" tells the user exactly where to work.

Then, in order: fatal defects -> important weaknesses -> fact-check table (with
corrections) -> what is genuinely good (keep it; do not flatter) -> missing
chapters -> revised action plan -> verdict.

Order the revised action plan as: **defenses -> cheapest validation ->
recompute the model with measured values -> only then build and sell.** Plans
habitually put "build the landing page" in week 1; that maximizes rework when
the premise turns out false.

Deliver files at concrete absolute paths.

### Delivering the artifacts

A review whose files never arrive is a review that did not happen. This user
reacts strongly to silent delivery failures and will not accept "copy it from
the chat" as a resolution.

- **Do not announce "download links" as an accomplished fact.** Write the
  `MEDIA:` line and describe what each file is, but treat arrival as unproven
  until the user confirms or you have delivered to that path before in this
  session.
- **If the user says no link appeared, do not re-emit the same path.** Emitting
  it again produces the same nothing. Diagnose where the runtime can actually
  write, move the files, and re-deliver from there.
- **Durable fallback: publish out of the filesystem entirely.** This user has
  Google Workspace OAuth configured, so a Sheet/Doc URL is reachable no matter
  which filesystem or container the agent happens to be running in. For a
  feasibility model specifically, a Google Sheet is often the *better* primary
  deliverable anyway — live formulas, editable assumptions, no download step.
  See the `google-workspace` skill.
- Offer the fallback **as a concrete next action you will perform**, not as
  homework for the user.

## Pitfalls

- **Reviewing without Gate 0.** Constraints surfaced late invalidate the offer
  design and force a full rewrite.
- **New constraints can kill your own prior recommendations.** If a later turn
  adds "no meetings," recheck whether last turn's advice (e.g. "do a screen-
  share session") still stands. Say so explicitly rather than silently
  contradicting yourself.
- **Accepting a tier matrix as competitor analysis.**
- **Forgetting sales hours** in the effort model.
- **Presenting an infeasible plan as feasible** because the arithmetic was
  never run.
- **Softening a legal finding into a "consideration."** Criminal exposure and
  account termination are not nuance.
- **Flattery.** Name the genuinely strong parts precisely and briefly, then
  move on.
- **Only reporting failure.** When the model says "impossible," do a
  sensitivity pass and find the assumption set that *does* clear the ceiling —
  ship the feasible solution alongside the verdict.
- **Cutting a constrained capability as pure loss.** Constraints often invert
  into differentiation ("no infra access" = a trust guarantee competitors
  cannot offer; a bad timezone = overnight delivery). Look for the inversion
  before declaring a weakness.
- **Declaring delivery done without evidence.** Presenting a list of download
  links the user cannot see burns the ending of an otherwise strong review.
  See "Delivering the artifacts" above.

## User Preferences (Koudai Ishigame)

- Respond in **Japanese**; keep English only for contract text, code, and
  direct quotes from sources.
- Blunt and specific. Graded verdicts, tables, numbers. No hedging, no padding.
- **Verify claims against official docs and flag misinformation** — an explicit
  standing instruction.
- Deliver files at concrete absolute paths (`MEDIA:/abs/path`). Never say
  "copy this from the chat."
- Prefers fixing root causes over workarounds.
- Wants recurring procedures captured as skills.

## Supporting Files

- `references/feasibility-model.md` — funnel/capacity model design, the
  headless formula-verification technique, and the sensitivity-analysis loop
- `references/legal-risk-checklist.md` — solo/cross-border service business
  legal gates: liability, chargebacks, insurance reality, contract clauses
- `templates/kpi_funnel_model.py` — working openpyxl generator for an
  8-sheet feasibility workbook with a pass/fail verdict cell
