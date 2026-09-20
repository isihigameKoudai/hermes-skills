# Legal & Risk Checklist — Solo / Cross-Border Service Businesses

Not legal advice. These are the gates a plan must *address*; the user still
needs one lawyer pass before the first paid contract (a liability-cap +
governing-law review is cheap and is the highest-ROI spend in the plan).

## 1. Legality of the acquisition tactic (check this first)

Growth plans routinely propose tactics that are crimes.

**Red flag pattern:** "find vulnerabilities in prospects' live apps and DM
them the findings." Probing a stranger's system without authorization can
satisfy computer-misuse offences (US CFAA, UK Computer Misuse Act). US case
law narrowed "exceeds authorized access" (*Van Buren*, 2021), but bypassing
authentication to reach someone else's data remains squarely exposed — and
good-faith researchers still receive legal threats routinely.

Redesign to **consent-first**:

- Publicly solicit applicants instead of cold-probing. "Free review for 3
  founders — reply to apply" flips unauthorized access into invited access.
- **Written permission before looking at anything**, captured in the intake
  form.
- **Passive observation only** — what is visible in a public bundle or
  DevTools. No scanning, no brute force, no auth bypass.
- Test only against an account you created yourself. If you can reach another
  record, **stop immediately**; do not view, do not store.
- Mask everything in any artifact; never show real data.
- Open every artifact with a non-intrusive / no-data-retrieved statement.
- Delete recordings on a stated schedule.
- **Best structural fix:** ship an open-source local scanner and have the
  applicant run it on their own machine and send you the output. You never
  touch their system, the effort collapses, and the tool becomes the inbound
  channel.

Also check platform ToS before calling a channel a "primary battleground":
self-promotion limits on community forums (10:1-style rules) and product
`#help` channels get accounts banned. Reclassify those as **observation posts**
— find who is struggling, approach elsewhere.

## 2. "Prepaid means zero risk" is false

Chargebacks pierce a no-refund policy. A cardholder disputing "service not as
described" pulls the funds regardless of your terms, dispute fees can apply
either way, and elevated dispute rates put the payment account itself at risk.
For a solo business doing ~10 transactions/month, a single dispute can breach
the threshold.

Mitigations to require in the plan:

- Replace "no refunds" with **"any agreed scope item not delivered is redone
  free"**. Lowers buyer anxiety *and* removes the freeloader path better than a
  subjective-satisfaction refund would.
- Standardize evidence: written scope approval at a citable URL, delivery
  artifact links, work log, correspondence.
- Enable fraud screening; consider invoice/bank transfer above a threshold.
- Monitor the dispute rate as a named risk-register line.

## 3. Insurance reality (individual operators)

Do **not** frame this as "cross-border freelancing is too risky." Frame it as:
uninsured means the **contract** is the only shield, so the contract must be
written properly.

- Most solo developers worldwide operate uninsured; this is normal, not
  disqualifying.
- E&O / professional-indemnity products skew toward companies, and coverage
  for foreign clients under foreign law needs case-by-case confirmation.
- **Insurability improves by narrowing scope.** A delivery model that never
  touches production, never merges/deploys, and never holds credentials
  structurally eliminates the categories that generate large claims. Say so —
  it is a genuine risk reduction, and a sales asset.
- Revisit incorporation + insurance once revenue stabilizes.

## 4. Terminology discipline

"Audit," "certification," "penetration test" carry regulatory meaning
(SOC 2 / ISO 27001 / PCI DSS). Using them casually raises the client's
expectations and the provider's exposure simultaneously. Prefer
"code review" / "codebase review," and state explicitly in the contract that
the work is **not** a certification and may not be represented as one.

## 5. Contract clauses the plan must name

| Clause | Why |
|---|---|
| **Liability cap = fees paid** | The single most important clause for an uninsured operator |
| **No-warranty / as-is** | Especially: no guarantee the code is free of vulnerabilities |
| **Exclusion of indirect damages** | Lost profit, lost data, fines, third-party claims |
| **Scope definition + approval** | Agreed item list approved in writing *before* work starts |
| **Deemed approval / deemed acceptance** | Protects against a silent client stalling the engagement |
| **Mutual NDA** | Clients cannot hand over code without it |
| **IP assignment on full payment** | Plus a licence back for your pre-existing tools/templates |
| **AI-tool disclosure & consent** | If client code goes into an AI tool, get consent and warrant zero-retention/no-training configuration. Silent use is a confidentiality breach |
| **Client responsibilities** | Review, merge, deploy, rotate exposed credentials, keep backups |
| **Indemnity** | For client deployment decisions and failure to follow the runbook |
| **Force majeure** | Illness in a one-person business |
| **Governing law + dispute resolution** | Expect pushback on a home-jurisdiction arbitration clause; it is primarily a deterrent. Falling back to a negotiation-only clause is an acceptable trade |
| **Tax** | Withholding, W-8BEN-style forms, cross-border service-tax treatment, FX exposure |

Where the contract is accepted by checkout, put the terms URL in the payment
link so **payment constitutes acceptance**, and mirror a short plain-language
version next to the pricing table.

## 6. Risks a solo plan usually omits

- **Key-person risk** — illness stops all revenue and breaches any SLA. Cap
  retainer clients; arrange a backup peer.
- **Account bans** — single-channel dependency. Diversify.
- **FX** — a double-digit swing moves take-home materially.
- **Demand decay** — if the hook depends on information asymmetry, check
  whether the platform/vendor is closing that gap with built-in tooling.
- **Async-specific expectation mismatch** — with no calls, a written
  scope-approval protocol is the only defence against disputes. Make it a
  hard gate: no approval, no work.
