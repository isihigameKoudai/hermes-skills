#!/usr/bin/env python3
"""Feasibility / KPI funnel workbook generator.

Copy and adapt. Produces an 8-sheet workbook whose single verdict cell
recomputes when the user edits any assumption.

Design rules this template encodes (do not break them when adapting):
  1. EVERY input lives on 01_assumptions; other sheets reference it by
     absolute ref collected in the ``P`` dict. Nothing hardcoded elsewhere.
  2. Sales hours are a first-class line in the effort model.
  3. One verdict cell compares weekly hours to the capacity ceiling and
     names the levers in priority order.
  4. 05_actuals derives MEASURED conversion rates and diffs them against
     the assumed ones, so the model can be re-based on data.

    pip install openpyxl
    python kpi_funnel_model.py out.xlsx

Then verify formulas actually evaluate (openpyxl never calculates) --
see references/feasibility-model.md for the `formulas` checker recipe.
"""
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = sys.argv[1] if len(sys.argv) > 1 else "feasibility_model.xlsx"

HDR_FONT = Font(bold=True, color="FFFFFF", size=11)
HDR_FILL = PatternFill("solid", fgColor="1F3864")
SUB_FILL = PatternFill("solid", fgColor="2E75B6")
IN_FILL = PatternFill("solid", fgColor="FFF2CC")   # yellow: user input
CALC_FILL = PatternFill("solid", fgColor="E2EFDA")  # green: formula
WARN_FILL = PatternFill("solid", fgColor="FCE4D6")  # orange: verdict
THIN = Border(*[Side(style="thin", color="BFBFBF")] * 4)
BOLD = Font(bold=True)

wb = Workbook()


def head(ws, row, cells, fill=HDR_FILL):
    for i, v in enumerate(cells, 1):
        c = ws.cell(row=row, column=i, value=v)
        c.font, c.fill, c.border = HDR_FONT, fill, THIN
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def put(ws, r, c, v, fill=None, fmt=None, bold=False):
    cell = ws.cell(row=r, column=c, value=v)
    if fill:
        cell.fill = fill
    if fmt:
        cell.number_format = fmt
    if bold:
        cell.font = BOLD
    cell.border = THIN
    return cell


# ---------------------------------------------------------------- 00 how to use
ws = wb.active
ws.title = "00_how-to-use"
ws.column_dimensions["A"].width = 4
ws.column_dimensions["B"].width = 108
for i, (text, is_h) in enumerate([
    ("Feasibility / KPI model", True),
    ("", False),
    ("COLOURS", True),
    ("  yellow = your input. Edit only these.", False),
    ("  green  = formula, auto-calculated.", False),
    ("  orange = verdict / warning.", False),
    ("", False),
    ("RULES", True),
    ("  1. Fill 01_assumptions with your own estimates.", False),
    ("  2. If 02_funnel's verdict says NG, the plan is broken BEFORE you start.", False),
    ("     Change assumptions until it reads OK. Do not execute an NG plan.", False),
    ("  3. After the first validation cycle, OVERWRITE assumptions with measured", False),
    ("     values from 05_actuals. Assumed rates are hypotheses, not facts.", False),
    ("  4. Log real numbers weekly in 05_actuals. Never log estimates there.", False),
    ("  5. Check 07_exit-criteria monthly. It exists so the decision is numeric.", False),
], start=1):
    c = ws.cell(row=i, column=2, value=text)
    if is_h:
        c.font = Font(bold=True, size=13 if i == 1 else 11, color="1F3864")

# ---------------------------------------------------------------- 01 assumptions
ws = wb.create_sheet("01_assumptions")
for col, w in zip("ABCDE", [4, 44, 16, 14, 58]):
    ws.column_dimensions[col].width = w
ws["B1"] = "Assumptions (edit yellow cells only)"
ws["B1"].font = Font(bold=True, size=13, color="1F3864")
head(ws, 3, ["", "Item", "Value", "Unit", "Note"])

ASSUMPTIONS = [
    ("== Pricing ==", None, None, None),
    ("Tier A price", 199, "USD", "Entry / diagnostic. A lead magnet, not a revenue line"),
    ("Tier B price", 899, "USD", "Core offer"),
    ("Tier C price", 2400, "USD", "Premium"),
    ("Retainer monthly", 1800, "USD", ""),
    ("== Delivery hours ==", None, None, None),
    ("Tier A hours", 2.5, "h", ""),
    ("Tier B hours", 9, "h", ""),
    ("Tier C hours", 24, "h", ""),
    ("Retainer hours/month", 10, "h", "Real load, not the advertised allowance"),
    ("== Conversion rates (MEASURE THESE) ==", None, None, None),
    ("Free-offer -> Tier A", 0.25, "rate", "[assumed] until validated"),
    ("Tier A -> upgrade", 0.40, "rate", "[assumed]"),
    ("Cold DM reply rate", 0.20, "rate", "[assumed]"),
    ("DM reply -> free offer", 0.40, "rate", "[assumed]"),
    ("Inbound share of free offers", 0.90, "rate", "KEY LEVER: content/OSS vs cold outreach"),
    ("Applicants per content piece", 6.0, "count", ""),
    ("== Sales effort ==", None, None, None),
    ("Free offer hours (manual)", 2.5, "h", "Be honest here; this is routinely underestimated"),
    ("Free offer hours (tool-assisted)", 0.5, "h", "Applicant self-serves; you review output"),
    ("Automation rate of free offer", 0.85, "rate", "KEY LEVER"),
    ("Hours per DM", 0.15, "h", "Including prospect research"),
    ("Hours per content piece", 3.0, "h", ""),
    ("== Costs & FX ==", None, None, None),
    ("Payment fee rate", 0.039, "rate", "Processor + FX spread"),
    ("Fixed monthly cost", 150, "USD", ""),
    ("FX rate", 150, "JPY/USD", ""),
    ("Post-tax take-home ratio", 0.70, "rate", ""),
    ("== Capacity ==", None, None, None),
    ("Weekly hours ceiling", 38, "h", "HARD CONSTRAINT. Any plan above this is broken"),
]

P, r = {}, 4
for name, val, unit, note in ASSUMPTIONS:
    if val is None:
        c = put(ws, r, 2, name, SUB_FILL)
        c.font = HDR_FONT
        for cc in range(3, 6):
            put(ws, r, cc, "", SUB_FILL)
    else:
        put(ws, r, 2, name)
        cell = put(ws, r, 3, val, IN_FILL)
        if unit == "rate":
            cell.number_format = "0.0%"
        put(ws, r, 4, unit)
        put(ws, r, 5, note)
        P[name] = f"'01_assumptions'!$C${r}"
    r += 1

# ---------------------------------------------------------------- 02 funnel
ws = wb.create_sheet("02_funnel")
for col, w in zip("ABCDE", [4, 46, 18, 12, 54]):
    ws.column_dimensions[col].width = w
ws["B1"] = "Reverse calculation from the revenue target (auto verdict)"
ws["B1"].font = Font(bold=True, size=13, color="1F3864")

head(ws, 3, ["", "Target mix (yellow = input)", "Count", "Revenue", "Note"])
MIX = [("Tier B deals", 2, P["Tier B price"]),
       ("Tier C deals", 1, P["Tier C price"]),
       ("Retainer clients", 1, P["Retainer monthly"]),
       ("Tier A standalone", 2, P["Tier A price"])]
r = first = 4
for name, cnt, price in MIX:
    put(ws, r, 2, name)
    put(ws, r, 3, cnt, IN_FILL)
    put(ws, r, 4, f"=C{r}*{price}", CALC_FILL, "$#,##0")
    r += 1
last = r - 1

put(ws, r, 2, "Gross revenue", bold=True)
put(ws, r, 4, f"=SUM(D{first}:D{last})", CALC_FILL, "$#,##0", True)
gross = f"'02_funnel'!$D${r}"
r += 1
put(ws, r, 2, "Payment fees")
put(ws, r, 4, f"=-{gross}*{P['Payment fee rate']}", CALC_FILL, "$#,##0")
fee = r
r += 1
put(ws, r, 2, "Fixed costs")
put(ws, r, 4, f"=-{P['Fixed monthly cost']}", CALC_FILL, "$#,##0")
fix = r
r += 1
put(ws, r, 2, "Net (pre-tax)", bold=True)
put(ws, r, 4, f"={gross}+D{fee}+D{fix}", CALC_FILL, "$#,##0", True)
net = f"'02_funnel'!$D${r}"
r += 1
put(ws, r, 2, "Take-home (local currency, post-tax est.)", bold=True)
put(ws, r, 4, f"={net}*{P['FX rate']}*{P['Post-tax take-home ratio']}", CALC_FILL, "#,##0", True)

r += 3
head(ws, r, ["", "Required volume", "Count", "Hours", "Note"])
r += 1
s = r
new_deals = f"(C{first}+C{first + 1}+C{first + 2})"
free_h = (f"({P['Automation rate of free offer']}*{P['Free offer hours (tool-assisted)']}"
          f"+(1-{P['Automation rate of free offer']})*{P['Free offer hours (manual)']})")
FUNNEL = [
    ("New deals needed", f"={new_deals}", None, "Tier B + C + retainer"),
    ("Acquired via Tier A", f"={new_deals}", None, "Assume all upgrade through Tier A"),
    ("-> Tier A orders needed", f"={new_deals}/{P['Tier A -> upgrade']}", None, ""),
    ("-> Free offers needed", f"=C{s + 2}/{P['Free-offer -> Tier A']}", f"=C{s + 3}*{free_h}",
     "Automation rate drives this hour figure"),
    ("   inbound (content/OSS)", f"=C{s + 3}*{P['Inbound share of free offers']}", None, "No DM effort"),
    ("   outbound (DM)", f"=C{s + 3}*(1-{P['Inbound share of free offers']})", None, ""),
    ("-> Content pieces needed", f"=C{s + 4}/{P['Applicants per content piece']}",
     f"=C{s + 6}*{P['Hours per content piece']}", ""),
    ("-> DM replies needed", f"=C{s + 5}/{P['DM reply -> free offer']}", None, ""),
    ("-> DMs to send", f"=C{s + 7}/{P['Cold DM reply rate']}", f"=C{s + 8}*{P['Hours per DM']}", ""),
]
for name, f1, f2, note in FUNNEL:
    put(ws, r, 2, name)
    put(ws, r, 3, f1, CALC_FILL, "#,##0.0")
    put(ws, r, 4, f2 or "", CALC_FILL, "#,##0.0")
    put(ws, r, 5, note)
    r += 1

put(ws, r, 2, "Sales hours total", bold=True)
put(ws, r, 4, f"=D{s + 3}+D{s + 6}+D{s + 8}", CALC_FILL, "#,##0.0", True)
sales_h = f"'02_funnel'!$D${r}"
r += 1
put(ws, r, 2, "Delivery hours total", bold=True)
put(ws, r, 4,
    f"=C{first}*{P['Tier B hours']}+C{first + 1}*{P['Tier C hours']}"
    f"+C{first + 2}*{P['Retainer hours/month']}+(C{first + 3}+C{s + 2})*{P['Tier A hours']}",
    CALC_FILL, "#,##0.0", True)
deliv_h = f"'02_funnel'!$D${r}"
r += 1
put(ws, r, 2, "Admin / support (15%)", bold=True)
put(ws, r, 4, f"=({sales_h}+{deliv_h})*0.15", CALC_FILL, "#,##0.0")
admin_h = f"'02_funnel'!$D${r}"
r += 1
put(ws, r, 2, "TOTAL monthly hours", bold=True)
put(ws, r, 4, f"={sales_h}+{deliv_h}+{admin_h}", CALC_FILL, "#,##0.0", True)
total_h = f"'02_funnel'!$D${r}"
r += 1
put(ws, r, 2, "WEEKLY hours", bold=True)
put(ws, r, 4, f"={total_h}/4.33", CALC_FILL, "#,##0.0", True)
week_h = f"'02_funnel'!$D${r}"
r += 2

cap = P["Weekly hours ceiling"]
put(ws, r, 2, "VERDICT", bold=True)
put(ws, r, 3, f'=IF({week_h}>{cap},"NG: INFEASIBLE","OK")', WARN_FILL, None, True)
put(ws, r, 5,
    f'=IF({week_h}>{cap},'
    f'"Over the ceiling. Levers in priority order: 1) raise automation rate of the free offer '
    f'2) cut entry-tier delivery hours via standardisation 3) raise prices 4) lower target volume. '
    f'Do 1 and 2 first.",'
    f'"Feasible. But every conversion rate here is a hypothesis - overwrite 01_assumptions with '
    f'measured values after the first validation cycle.")', WARN_FILL)

# ---------------------------------------------------------------- 03 effective hourly
ws = wb.create_sheet("03_effective-hourly")
for col, w in zip("ABCDEFGH", [4, 26, 12, 12, 12, 14, 14, 46]):
    ws.column_dimensions[col].width = w
ws["B1"] = "Effective hourly rate per offer (are you underpricing?)"
ws["B1"].font = Font(bold=True, size=13, color="1F3864")
head(ws, 3, ["", "Offer", "Price", "Deliv h", "Sales h", "After fees", "Eff. $/h", "Check"])
OFFERS = [("Tier A standalone", P["Tier A price"], P["Tier A hours"], 3.0),
          ("Tier A -> B (net)", P["Tier B price"], f"({P['Tier A hours']}+{P['Tier B hours']})", 3.0),
          ("Tier B direct", P["Tier B price"], P["Tier B hours"], 5.0),
          ("Tier C", P["Tier C price"], P["Tier C hours"], 6.0),
          ("Retainer", P["Retainer monthly"], P["Retainer hours/month"], 1.0)]
r = 4
for name, price, dh, sh in OFFERS:
    put(ws, r, 2, name)
    put(ws, r, 3, f"={price}", CALC_FILL, "$#,##0")
    put(ws, r, 4, f"={dh}", CALC_FILL, "0.0")
    put(ws, r, 5, sh, IN_FILL, "0.0")
    put(ws, r, 6, f"=C{r}*(1-{P['Payment fee rate']})", CALC_FILL, "$#,##0")
    put(ws, r, 7, f"=F{r}/(D{r}+E{r})", CALC_FILL, "$#,##0", True)
    put(ws, r, 8,
        f'=IF(G{r}<50,"BELOW your claimed positioning band - raise price or cut hours",'
        f'IF(G{r}<75,"Acceptable but at the floor","OK"))', WARN_FILL)
    r += 1
r += 1
ws.cell(row=r, column=2,
        value="Set the band to whatever the plan claims for itself. An offer below its own "
              "stated positioning is an internal contradiction.").font = Font(italic=True, color="C00000")

# ---------------------------------------------------------------- 04 capacity
ws = wb.create_sheet("04_capacity")
for col, w in zip("ABCDE", [4, 40, 14, 14, 50]):
    ws.column_dimensions[col].width = w
ws["B1"] = "Capacity ceiling decomposition"
ws["B1"].font = Font(bold=True, size=13, color="1F3864")
head(ws, 3, ["", "Constraint", "Value", "Unit", "Basis"])
CAPS = [("Weekly hours ceiling", f"={P['Weekly hours ceiling']}", "h", "From 01_assumptions"),
        ("Monthly hours", f"={P['Weekly hours ceiling']}*4.33", "h", ""),
        ("Delivery-available (60%)", "=C5*0.6", "h", "Other 40% is sales + admin"),
        ("-> max Tier B deals", f"=C6/{P['Tier B hours']}", "count", "If everything were Tier B"),
        ("-> max Tier C deals", f"=C6/{P['Tier C hours']}", "count", ""),
        ("Retainer cap", 2, "count", "Enforce. Overrunning this causes late delivery"),
        ("Hours consumed by retainers", f"=C9*{P['Retainer hours/month']}", "h", ""),
        ("Remaining for new work", "=C6-C10", "h", ""),
        ("-> new Tier B possible", f"=C11/{P['Tier B hours']}", "count", "Realistic capacity")]
r = 4
for name, f, unit, note in CAPS:
    put(ws, r, 2, name)
    put(ws, r, 3, f, IN_FILL if isinstance(f, int) else CALC_FILL, "#,##0.0")
    put(ws, r, 4, unit)
    put(ws, r, 5, note)
    r += 1

# ---------------------------------------------------------------- 05 actuals
ws = wb.create_sheet("05_actuals")
COLS = ["Wk", "Period", "Prospects", "DMs", "Replies", "Free offers", "Tier A",
        "Tier B", "Tier C", "Retainer", "Revenue", "Deliv h", "Sales h", "Total h", "Notes"]
for i, w in enumerate([6, 16, 12, 10, 10, 12, 10, 10, 10, 11, 12, 9, 9, 9, 38], 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws["A1"] = "Log REAL numbers weekly. Never estimates."
ws["A1"].font = Font(bold=True, size=13, color="1F3864")
head(ws, 3, COLS)
for i in range(1, 27):
    r = 3 + i
    put(ws, r, 1, i, IN_FILL)
    for c in range(2, 15):
        put(ws, r, c, "", IN_FILL)
    put(ws, r, 14, f"=L{r}+M{r}", CALC_FILL, "0.0")
    put(ws, r, 15, "", IN_FILL)
TOT = 30
put(ws, TOT, 1, "TOTAL", bold=True)
for c in range(3, 15):
    L = get_column_letter(c)
    put(ws, TOT, c, f"=SUM({L}4:{L}29)", CALC_FILL, "#,##0.0", True)

r = TOT + 2
head(ws, r, ["", "Measured rate", "Actual", "Assumed", "Delta", "Action"], SUB_FILL)
ws.column_dimensions["F"].width = 60
r += 1
for name, f, base in [
    ("DM reply rate", "=IF(D30=0,\"\",E30/D30)", P["Cold DM reply rate"]),
    ("Reply -> free offer", "=IF(E30=0,\"\",F30/E30)", P["DM reply -> free offer"]),
    ("Free offer -> Tier A", "=IF(F30=0,\"\",G30/F30)", P["Free-offer -> Tier A"]),
    ("Tier A -> upgrade", "=IF(G30=0,\"\",(H30+I30)/G30)", P["Tier A -> upgrade"]),
]:
    put(ws, r, 2, name)
    put(ws, r, 3, f, CALC_FILL, "0.0%")
    put(ws, r, 4, f"={base}", CALC_FILL, "0.0%")
    put(ws, r, 5, f'=IF(C{r}="","",C{r}-D{r})', CALC_FILL, "0.0%")
    put(ws, r, 6,
        f'=IF(C{r}="","insufficient data",'
        f'IF(C{r}<D{r}*0.6,"Assumption too optimistic. Overwrite 01_assumptions and re-check 02_funnel",'
        f'IF(C{r}>D{r}*1.2,"Beating plan - concentrate effort on this channel","Roughly as planned")))',
        WARN_FILL)
    r += 1

# ---------------------------------------------------------------- 06 12-month P&L
ws = wb.create_sheet("06_12mo-pl")
ws.column_dimensions["A"].width = 4
ws.column_dimensions["B"].width = 30
for i in range(3, 16):
    ws.column_dimensions[get_column_letter(i)].width = 11
ws["B1"] = "12-month cashflow (yellow = deal counts)"
ws["B1"].font = Font(bold=True, size=13, color="1F3864")
head(ws, 3, ["", "Item"] + [f"M{m}" for m in range(1, 13)] + ["Total"])
RAMP = {
    "Tier A count": [0, 2, 3, 4, 5, 5, 6, 6, 6, 6, 6, 6],
    "Tier B count": [0, 0, 1, 1, 2, 3, 3, 4, 4, 4, 4, 4],
    "Tier C count": [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2],
    "Retainer count": [0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2],
}
r, rows = 4, {}
for name, vals in RAMP.items():
    put(ws, r, 2, name)
    for i, v in enumerate(vals):
        put(ws, r, 3 + i, v, IN_FILL)
    put(ws, r, 15, f"=SUM(C{r}:N{r})", CALC_FILL, "#,##0")
    rows[name] = r
    r += 1
r += 1
put(ws, r, 2, "Revenue", bold=True)
for i in range(12):
    col = get_column_letter(3 + i)
    put(ws, r, 3 + i,
        f"={col}{rows['Tier A count']}*{P['Tier A price']}+{col}{rows['Tier B count']}*{P['Tier B price']}"
        f"+{col}{rows['Tier C count']}*{P['Tier C price']}+{col}{rows['Retainer count']}*{P['Retainer monthly']}",
        CALC_FILL, "$#,##0")
put(ws, r, 15, f"=SUM(C{r}:N{r})", CALC_FILL, "$#,##0", True)
rev = r
r += 1
put(ws, r, 2, "Payment fees")
for i in range(12):
    col = get_column_letter(3 + i)
    put(ws, r, 3 + i, f"=-{col}{rev}*{P['Payment fee rate']}", CALC_FILL, "$#,##0")
f1 = r
r += 1
put(ws, r, 2, "Fixed costs")
for i in range(12):
    put(ws, r, 3 + i, f"=-{P['Fixed monthly cost']}", CALC_FILL, "$#,##0")
f2 = r
r += 1
put(ws, r, 2, "Setup costs (legal review etc.)")
for i in range(12):
    put(ws, r, 3 + i, -400 if i == 0 else 0, IN_FILL, "$#,##0")
f3 = r
r += 1
put(ws, r, 2, "Monthly profit", bold=True)
for i in range(12):
    col = get_column_letter(3 + i)
    put(ws, r, 3 + i, f"={col}{rev}+{col}{f1}+{col}{f2}+{col}{f3}", CALC_FILL, "$#,##0", True)
put(ws, r, 15, f"=SUM(C{r}:N{r})", CALC_FILL, "$#,##0", True)
prof = r
r += 1
put(ws, r, 2, "Cumulative", bold=True)
put(ws, r, 3, f"=C{prof}", CALC_FILL, "$#,##0", True)
for i in range(1, 12):
    put(ws, r, 3 + i,
        f"={get_column_letter(2 + i)}{r}+{get_column_letter(3 + i)}{prof}",
        CALC_FILL, "$#,##0", True)

# ---------------------------------------------------------------- 07 exit criteria
ws = wb.create_sheet("07_exit-criteria")
for col, w in zip("ABCDE", [4, 34, 18, 18, 56]):
    ws.column_dimensions[col].width = w
ws["B1"] = "Exit / pivot criteria (decide numerically, not emotionally)"
ws["B1"].font = Font(bold=True, size=13, color="1F3864")
head(ws, 3, ["", "Checkpoint", "Threshold", "Actual", "Verdict"])
CRIT = [
    ("Day 90: paid deals", ">= 3", 0, 3, "below",
     "Miss -> change channel wholesale. Drop outbound, go all-in on content + OSS."),
    ("Day 150: monthly revenue", ">= $2,000", 0, 2000, "below",
     "Miss -> exit, or change market (e.g. domestic, where the language constraint disappears)."),
    ("Ongoing: dispute rate", "< 1.0%", 0, 0.01, "above",
     "Breach -> payment account at risk. Revisit the prepay model immediately."),
    ("Ongoing: actual weekly hours", "<= ceiling", 0, 38, "above",
     "Breach -> raise prices or take fewer deals. Burnout -> quality drop -> disputes -> dead business."),
    ("Ongoing: free-offer conversion", ">= 5%", 0, 0.05, "below",
     "Miss -> the hook itself is not working. Rebuild the offer, not the funnel."),
]
r = 4
for name, thresh, actual, th, direction, _ in CRIT:
    put(ws, r, 2, name)
    put(ws, r, 3, thresh)
    c = put(ws, r, 4, actual, IN_FILL)
    if "%" in thresh:
        c.number_format = "0.00%"
    op = "<" if direction == "below" else ">"
    put(ws, r, 5, f'=IF(D{r}{op}{th},"ACTION REQUIRED","OK")', WARN_FILL, None, True)
    r += 1
r += 1
ws.cell(row=r, column=2, value="Actions").font = Font(bold=True, size=12, color="C00000")
r += 1
for name, _, _, _, _, action in CRIT:
    ws.cell(row=r, column=2, value=name).font = BOLD
    ws.cell(row=r, column=3, value=action).alignment = Alignment(wrap_text=True)
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
    r += 1

for s_ in wb.worksheets:
    s_.freeze_panes = "A1" if s_.title == "00_how-to-use" else "A4"
    s_.sheet_view.showGridLines = False

wb.save(OUT)
print(f"saved {OUT}")
