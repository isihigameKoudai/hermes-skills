# Building and Verifying a Feasibility Model

The deliverable that separates a real review from an opinion. Ship a workbook
whose assumptions the user can change and whose verdict recomputes itself.

## Why a spreadsheet and not prose

- The user can disagree with an assumption and immediately see the consequence.
- It forces you to actually do the arithmetic. Asserting "this looks tight" is
  how a plan needing 121 hrs/week gets shipped as achievable.
- It survives the session. Prose review does not.

## Sheet layout that works (8 sheets)

| Sheet | Purpose |
|---|---|
| `00_how-to-use` | Colour legend, update cadence, the one rule: overwrite assumptions with measured values after the first validation cycle |
| `01_assumptions` | **Every** input in one place. All other sheets reference these cells. Nothing hardcoded anywhere else |
| `02_funnel` | Top-down reverse calc + bottom-up hours + the PASS/FAIL verdict cell |
| `03_effective-hourly` | Per-offer `(price − fees) / (delivery + sales hours)`, with a verdict against the claimed positioning band |
| `04_capacity` | Ceiling decomposition: max deals by mix, how much retainers consume |
| `05_actuals` | Weekly log. Auto-computes MEASURED conversion rates and diffs them against the assumed ones |
| `06_12mo-pl` | Monthly cashflow, cumulative profit |
| `07_exit-criteria` | Numeric thresholds with auto-firing verdict cells |

Colour convention: **yellow = user input**, **green = formula**, **orange =
verdict/warning**. State it on sheet 00. Users will not read a model they
cannot tell how to edit.

## Non-negotiable structural rules

1. **One assumptions sheet.** Build a `{label: "'01_assumptions'!$C$12"}` dict
   while writing that sheet and reference it everywhere else. Otherwise
   changing an assumption silently fails to propagate.
2. **A single verdict cell** comparing weekly hours to the capacity ceiling,
   with an `IF()` that names the levers in priority order:
   `IF(week_h > cap, "NG. Levers in order: 1) ... 2) ... 3) ...", "OK ...")`
3. **Sales hours as a first-class line.** Omitting them is the classic defect.
4. **An actuals sheet that computes measured rates and compares to assumed.**
   The whole point is replacing guesses with data at the first opportunity.

## Verifying the formulas actually evaluate

openpyxl never calculates. A workbook full of `=` strings can be completely
broken and look fine. Verify headlessly:

```bash
pip install formulas
```

```python
import formulas, warnings, re
warnings.filterwarnings('ignore')
sol = formulas.ExcelModel().loads('model.xlsx').finish().calculate()

pat = re.compile(r"'([^']*(?:funnel|hourly|capacity))'!([A-Z]+)(\d+)$")
out = {}
for key in sol:
    m = pat.search(key)
    if m:
        try:
            out[(m.group(1), m.group(2), int(m.group(3)))] = sol[key].value[0, 0]
        except Exception:
            pass
```

Then join against `openpyxl.load_workbook()` row labels and print
`label -> value` so the numbers are readable rather than a wall of cell refs.

Gotchas:
- Keys are uppercased and prefixed `'[FILE.XLSX]SheetName'!A1`. Match on the
  suffix, not equality.
- Values are numpy arrays — index `[0, 0]`.
- Regex-escape or avoid `\d` inside an f-string/shell heredoc; an unescaped
  quantifier throws `re.error: nothing to repeat`. Put the checker in its own
  `.py` file rather than a `-c` one-liner.
- `progress` bars go to stderr; filter with `grep -v "it/s"`.

Keep the checker as a standing `check.py` next to the generator and re-run it
after every assumption change.

## Sensitivity analysis: the part that produces the real answer

A verdict of "infeasible" is half a deliverable. Loop:

1. Run the model with the plan's own assumptions. Record the verdict.
2. If NG, change **one** assumption, re-run, record the delta.
3. Rank levers by hours saved.
4. Apply them in order until the verdict flips to OK.
5. Report the whole ladder, not just the endpoint.

Worked example from a real review (solo productized service):

| Step | Change | Weekly hours |
|---|---|---|
| Plan as written | — | **121 (NG)** |
| Lever 1 | Automate the free-audit step via a public OSS CLI (2.5h -> 0.5h, 85% automated) | 55 |
| Lever 2 | Standardize the entry-tier deliverable (4h -> 2.5h) | 41 |
| Lever 3 | Shift inbound share to 90% (content/OSS instead of cold DM) | **37 (OK)** |

The ladder, not the endpoint, is the insight: it showed that the OSS tool —
filed in the original plan as a minor marketing idea — was a **precondition
for the business existing at all**. No lever ranking, no finding.

Watch for levers that resolve several problems at once. Here, shipping the
scanner cut effort, became the inbound channel, and removed the criminal-
liability exposure (applicants run it on their own code, so you never touch a
stranger's system). Call these out explicitly — they reorder the roadmap.

## Reporting the numbers

- Show the plan's own assumptions failing first. It is the proof.
- Then the lever table.
- Then the feasible solution verbatim from the model output.
- State the currency conversion rate and the post-tax take-home ratio used.
- Label every conversion rate `[measured]` / `[benchmark]` / `[assumed]`, and
  say plainly that assumed rates are hypotheses requiring validation.
