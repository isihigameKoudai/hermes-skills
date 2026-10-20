"""Fiverr gig image generator (1280x769) — copy and edit the CONFIG block.

Why PIL: AI image models garble on-image text; PIL renders crisp, on-spec text.
Fonts: DejaVu / Liberation ship with most distros; no headless browser needed.
Layout: left text column + right mock "report" card (proves the deliverable).
Verify: load the output back and check for overflow/overlap before delivering.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 769
BG, PANEL, BORDER = "#0D1117", "#161B22", "#30363D"
WHITE, MUTED, ACCENT = "#E6EDF3", "#8B949E", "#58A6FF"
RED, AMBER, GREEN = "#F85149", "#D29922", "#3FB950"

FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# --------------------------- CONFIG ---------------------------
KICKER, KICKER2 = "CODE REVIEW", "/ AI-GENERATED APPS"
HEAD1, HEAD2 = "Find what AI", "left behind"
SUB1, SUB2 = "Security, auth & performance issues", "in your vibe-coded app"
CHIPS = ["Next.js + Supabase", "file:line findings", "100% async"]
CARD_FILE = "audit-report.md"
ROWS = [  # (label, color, title, file:line)
    ("HIGH", RED,   "RLS disabled on profiles", "supabase/migrations/0012.sql:14"),
    ("HIGH", RED,   "service_role key exposed", "lib/supabase/client.ts:9"),
    ("MED",  AMBER, "N+1 query in feed",        "app/api/posts/route.ts:22"),
    ("LOW",  GREEN, "no rate limiting",         "app/api/contact/route.ts:5"),
]
FOOT_A, FOOT_B = "23 findings", "· severity-ranked"
OUT = "gig1.png"
# --------------------------------------------------------------


def F(path, size):
    return ImageFont.truetype(path, size)


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 10, H], fill=ACCENT)  # left accent bar

# --- left: kicker, headline, sub, chips ---
d.text((70, 92), KICKER, font=F(FB, 26), fill=ACCENT)
kx = 70 + d.textlength(KICKER, font=F(FB, 26))
d.text((kx + 16, 92), KICKER2, font=F(FR, 26), fill=MUTED)

d.text((68, 146), HEAD1, font=F(FB, 88), fill=WHITE)
d.text((68, 246), HEAD2, font=F(FB, 88), fill=WHITE)
d.rectangle([72, 356, 168, 362], fill=ACCENT)

sub = "#ADBAC7"
d.text((70, 392), SUB1, font=F(FR, 30), fill=sub)
d.text((70, 432), SUB2, font=F(FR, 30), fill=sub)

x = 70
for c in CHIPS:
    f = F(FB, 21)
    w = d.textlength(c, font=f) + 40
    d.rounded_rectangle([x, 614, x + w, 660], radius=23, fill=PANEL, outline=BORDER, width=2)
    d.text((x + 20, 625), c, font=f, fill=WHITE)
    x += w + 14

# --- right: mock report card ---
cx, cy, cw, ch = 716, 104, 500, 561
d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=PANEL, outline=BORDER, width=2)
for i, c in enumerate(["#FF5F56", "#FFBD2E", "#27C93F"]):
    d.ellipse([cx + 28 + i * 26, cy + 30, cx + 42 + i * 26, cy + 44], fill=c)
d.text((cx + 118, cy + 24), CARD_FILE, font=F(FM, 21), fill=MUTED)
d.line([cx + 24, cy + 70, cx + cw - 24, cy + 70], fill=BORDER, width=2)

ry = cy + 92
for label, color, title, loc in ROWS:
    pf = F(FB, 17)
    pw = d.textlength(label, font=pf) + 26
    d.rounded_rectangle([cx + 28, ry + 2, cx + 28 + pw, ry + 30], radius=8, fill=color)
    d.text((cx + 41, ry + 8), label, font=pf, fill=BG)
    d.text((cx + 28, ry + 42), title, font=F(FB, 24), fill=WHITE)
    d.text((cx + 28, ry + 74), loc, font=F(FM, 17), fill=MUTED)
    ry += 108

d.line([cx + 24, cy + ch - 56, cx + cw - 24, cy + ch - 56], fill=BORDER, width=2)
d.text((cx + 28, cy + ch - 42), FOOT_A, font=F(FB, 22), fill=ACCENT)
d.text((cx + 176, cy + ch - 42), FOOT_B, font=F(FR, 22), fill=MUTED)

img.save(OUT, "PNG")
print("saved", img.size, "->", OUT)
