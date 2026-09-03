#!/usr/bin/env python3
"""Route B prototype: hyperlinked A5 digital planner shell (working brand: Leafline).

Original layouts and content. Generates a 13-page A5 PDF with a linked tab rail,
undated year/month/week/day pages, a left-hand mirrored daily page (the wedge),
notes, savings and habit trackers, and a printable punch-guide page.

Run: python3 generate_a5_planner.py  ->  leafline-a5-planner-prototype.pdf
"""
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

W, H = A5  # 148 x 210 mm
PAPER = HexColor("#FBF9F4")
INK = HexColor("#23262B")
SOFT = HexColor("#8D8A80")
FAINT = HexColor("#D8D3C6")
ACCENT = HexColor("#31555A")
ACCENT_SOFT = HexColor("#DDE6E4")

M = 13 * mm          # content margin
RAIL_W = 9 * mm      # tab rail width
TABS = [("YEAR", "sec-year"), ("MONTH", "sec-month"), ("WEEK", "sec-week"),
        ("DAY", "sec-day"), ("NOTES", "sec-notes"), ("TRACK", "sec-track")]

OUT = "leafline-a5-planner-prototype.pdf"


def base_page(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)


def rail(c, active, side="right"):
    """Linked tab rail on the outer edge. side='left' for the mirrored page."""
    x0 = W - RAIL_W if side == "right" else 0
    tab_h = 22 * mm
    top = H - 18 * mm
    for i, (label, dest) in enumerate(TABS):
        y = top - i * (tab_h + 2 * mm) - tab_h
        if i == active:
            c.setFillColor(ACCENT)
            c.roundRect(x0, y, RAIL_W, tab_h, 1.5 * mm, stroke=0, fill=1)
            c.setFillColor(PAPER)
        else:
            c.setFillColor(ACCENT_SOFT)
            c.roundRect(x0, y, RAIL_W, tab_h, 1.5 * mm, stroke=0, fill=1)
            c.setFillColor(ACCENT)
        c.saveState()
        c.translate(x0 + RAIL_W / 2 + 1.2 * mm, y + tab_h / 2)
        c.rotate(90)
        c.setFont("Helvetica-Bold", 6.2)
        c.drawCentredString(0, 0, label)
        c.restoreState()
        c.linkAbsolute(label, dest, (x0, y, x0 + RAIL_W, y + tab_h))


def header(c, title, sub=None, side="right"):
    x = M if side == "right" else M + RAIL_W - 4 * mm
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x, H - 16 * mm, title)
    if sub:
        c.setFillColor(SOFT)
        c.setFont("Helvetica", 7.5)
        c.drawString(x, H - 20.5 * mm, sub)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.1)
    c.line(x, H - 23 * mm, x + 30 * mm, H - 23 * mm)


def content_box(side="right"):
    """Usable area below header, respecting the rail side."""
    if side == "right":
        return M, W - RAIL_W - 4 * mm, M, H - 27 * mm  # x0, x1, y0, y1
    return M + RAIL_W - 4 * mm, W - M, M, H - 27 * mm


def dots(c, x0, x1, y0, y1, step=5 * mm):
    c.setFillColor(FAINT)
    y = y1
    while y >= y0:
        x = x0
        while x <= x1:
            c.circle(x, y, 0.55, stroke=0, fill=1)
            x += step
        y -= step


def wordmark(c, x, y, size=20):
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, "LEAFLINE")
    w = c.stringWidth("LEAFLINE", "Helvetica-Bold", size)
    c.setFillColor(ACCENT)
    c.circle(x + w + size * 0.22, y + size * 0.055, size * 0.115, stroke=0, fill=1)


# ---------------------------------------------------------------- pages
c = canvas.Canvas(OUT, pagesize=A5)
c.setTitle("Leafline A5 Planner (Prototype)")
c.setAuthor("Leafline")

# 1 · cover
base_page(c)
c.setFillColor(ACCENT)
c.rect(0, 0, W, 6 * mm, stroke=0, fill=1)
wordmark(c, M, H * 0.60, 26)
c.setFillColor(SOFT)
c.setFont("Helvetica", 9.5)
c.drawString(M, H * 0.60 - 9 * mm, "The modular A5 planner - digital edition")
c.setFont("Helvetica", 7.5)
c.drawString(M, H * 0.60 - 15 * mm, "Undated · hyperlinked · right- and left-handed layouts")
c.setFillColor(SOFT)
c.setFont("Helvetica-Bold", 7)
c.drawString(M, 12 * mm, "PROTOTYPE v0.1 - internal costing build, not for sale")
c.showPage()

# 2 · guide
base_page(c)
rail(c, -1)
header(c, "How this planner works", "Tap any tab on the edge of every page to jump between sections")
x0, x1, y0, y1 = content_box()
lines = [
    ("Built as a system, not a book.",
     "Six sections behave like the packs in a ring binder: swap what you use, ignore what you don't."),
    ("Undated on purpose.",
     "Start any week of any year. Write the dates yourself; skip a fortnight without wasting pages."),
    ("Made for both hands.",
     "Every writing page ships in right- and left-handed versions. The lefty page mirrors the layout and moves the tabs, so nothing sits under your writing hand."),
    ("Works where you write.",
     "Use it in GoodNotes, Notability or any PDF annotator, or print at 100% on A5 (or 2-up on A4) and file it in any A5 ring binder."),
]
y = y1 - 6 * mm
for t, b in lines:
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x0, y, t)
    c.setFillColor(INK)
    c.setFont("Helvetica", 7.8)
    yy = y - 4.6 * mm
    # naive wrap
    words, line = b.split(), ""
    for w_ in words:
        if c.stringWidth(line + " " + w_, "Helvetica", 7.8) > (x1 - x0):
            c.drawString(x0, yy, line.strip()); yy -= 3.8 * mm; line = w_
        else:
            line += " " + w_
    c.drawString(x0, yy, line.strip())
    y = yy - 8 * mm
c.showPage()

# 3 · year at a glance
base_page(c)
c.bookmarkPage("sec-year")
rail(c, 0)
header(c, "Year at a glance", "Undated - write the year once, use it every year")
x0, x1, y0, y1 = content_box()
cols, rows = 3, 4
cw = (x1 - x0 - 2 * 4 * mm) / cols
ch = (y1 - y0 - 10 * mm - 3 * 4 * mm) / rows
months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
for i, mo in enumerate(months):
    cx = x0 + (i % cols) * (cw + 4 * mm)
    cy = y1 - 8 * mm - (i // cols + 1) * ch - (i // cols) * 4 * mm
    c.setStrokeColor(FAINT); c.setLineWidth(0.7)
    c.roundRect(cx, cy, cw, ch, 1.5 * mm, stroke=1, fill=0)
    c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 7)
    c.drawString(cx + 2 * mm, cy + ch - 4 * mm, mo)
    c.setStrokeColor(FAINT); c.setLineWidth(0.5)
    for li in range(3):
        ly = cy + ch - 8 * mm - li * 3.6 * mm
        c.line(cx + 2 * mm, ly, cx + cw - 2 * mm, ly)
c.showPage()

# 4 · month
base_page(c)
c.bookmarkPage("sec-month")
rail(c, 1)
header(c, "Month of ____________", "Undated - number the days as you go")
x0, x1, y0, y1 = content_box()
days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
gw = (x1 - x0) / 7
c.setFont("Helvetica-Bold", 6); c.setFillColor(SOFT)
for i, d in enumerate(days):
    c.drawCentredString(x0 + gw * (i + 0.5), y1 - 4 * mm, d)
gtop = y1 - 6 * mm
gh = (gtop - y0 - 2 * mm) / 5
c.setStrokeColor(FAINT); c.setLineWidth(0.6)
for r in range(6):
    c.line(x0, gtop - r * gh, x1, gtop - r * gh)
for col in range(8):
    c.line(x0 + col * gw, gtop, x0 + col * gw, gtop - 5 * gh)
c.showPage()

# 5 · week left  (Mon-Thu)
base_page(c)
c.bookmarkPage("sec-week")
rail(c, 2)
header(c, "Week of ____________", "Spread 1 of 2 - Monday to Thursday")
x0, x1, y0, y1 = content_box()
rows4 = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"]
rh = (y1 - y0 - 4 * mm) / 4
for i, d in enumerate(rows4):
    ry = y1 - 2 * mm - (i + 1) * rh
    c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(x0, ry + rh - 3.5 * mm, d)
    c.setStrokeColor(FAINT); c.setLineWidth(0.5)
    for li in range(4):
        ly = ry + rh - 8 * mm - li * 4.6 * mm
        if ly > ry + 1 * mm:
            c.line(x0, ly, x1, ly)
c.showPage()

# 6 · week right (Fri-Sun + focus)
base_page(c)
rail(c, 2)
header(c, "Week of ____________", "Spread 2 of 2 - Friday to Sunday, and the week's focus")
x0, x1, y0, y1 = content_box()
rows3 = ["FRIDAY", "SATURDAY", "SUNDAY"]
rh = (y1 - y0 - 4 * mm) * 0.62 / 3
for i, d in enumerate(rows3):
    ry = y1 - 2 * mm - (i + 1) * rh
    c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(x0, ry + rh - 3.5 * mm, d)
    c.setStrokeColor(FAINT); c.setLineWidth(0.5)
    for li in range(3):
        ly = ry + rh - 8 * mm - li * 4.6 * mm
        if ly > ry + 1 * mm:
            c.line(x0, ly, x1, ly)
focus_top = y1 - 2 * mm - 3 * rh - 4 * mm
c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 6.5)
c.drawString(x0, focus_top, "THIS WEEK'S THREE")
c.setStrokeColor(FAINT)
for li in range(3):
    ly = focus_top - 6 * mm - li * 5.5 * mm
    c.setLineWidth(0.5); c.line(x0 + 6 * mm, ly, x1, ly)
    c.setStrokeColor(SOFT); c.setLineWidth(0.7)
    c.rect(x0, ly - 0.5 * mm, 3.2 * mm, 3.2 * mm, stroke=1, fill=0)
    c.setStrokeColor(FAINT)
c.showPage()


def daily(c, side):
    base_page(c)
    if side == "right":
        c.bookmarkPage("sec-day")
    rail(c, 3, side=side)
    header(c, "Day ____________", "Right-handed layout" if side == "right" else "Left-handed layout - mirrored so nothing sits under your hand", side=side)
    x0, x1, y0, y1 = content_box(side)
    col_split = x0 + (x1 - x0) * (0.42 if side == "right" else 0.58)
    sched_x0, sched_x1 = (x0, col_split - 3 * mm) if side == "right" else (col_split + 3 * mm, x1)
    task_x0, task_x1 = (col_split + 3 * mm, x1) if side == "right" else (x0, col_split - 3 * mm)
    # schedule 07-21
    c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(sched_x0, y1 - 3 * mm, "SCHEDULE")
    hours = list(range(7, 22))
    hh = (y1 - y0 - 8 * mm) / len(hours)
    for i, hr in enumerate(hours):
        ly = y1 - 7 * mm - i * hh
        c.setFillColor(SOFT); c.setFont("Helvetica", 5.5)
        c.drawString(sched_x0, ly, f"{hr:02d}")
        c.setStrokeColor(FAINT); c.setLineWidth(0.5)
        c.line(sched_x0 + 5 * mm, ly + 0.6 * mm, sched_x1, ly + 0.6 * mm)
    # priorities + tasks
    c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(task_x0, y1 - 3 * mm, "TOP THREE")
    for li in range(3):
        ly = y1 - 9 * mm - li * 6 * mm
        c.setStrokeColor(SOFT); c.setLineWidth(0.7)
        c.rect(task_x0, ly, 3.2 * mm, 3.2 * mm, stroke=1, fill=0)
        c.setStrokeColor(FAINT); c.setLineWidth(0.5)
        c.line(task_x0 + 5.5 * mm, ly, task_x1, ly)
    ty = y1 - 9 * mm - 3 * 6 * mm - 5 * mm
    c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(task_x0, ty, "ALSO TODAY")
    for li in range(7):
        ly = ty - 6 * mm - li * 5.2 * mm
        c.setStrokeColor(SOFT); c.setLineWidth(0.7)
        c.rect(task_x0, ly, 2.8 * mm, 2.8 * mm, stroke=1, fill=0)
        c.setStrokeColor(FAINT); c.setLineWidth(0.5)
        c.line(task_x0 + 5 * mm, ly, task_x1, ly)
    ny = ty - 6 * mm - 7 * 5.2 * mm - 5 * mm
    c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(task_x0, ny, "ONE LINE ON TODAY")
    c.setStrokeColor(FAINT); c.setLineWidth(0.5)
    c.line(task_x0, ny - 5 * mm, task_x1, ny - 5 * mm)
    c.showPage()


# 7 · daily RH, 8 · daily LH
daily(c, "right")
daily(c, "left")

# 9 · notes dot grid
base_page(c)
c.bookmarkPage("sec-notes")
rail(c, 4)
header(c, "Notes", "5 mm dot grid")
x0, x1, y0, y1 = content_box()
dots(c, x0, x1, y0, y1 - 3 * mm)
c.showPage()

# 10 · notes lined
base_page(c)
rail(c, 4)
header(c, "Notes", "Ruled")
x0, x1, y0, y1 = content_box()
c.setStrokeColor(FAINT); c.setLineWidth(0.5)
y = y1 - 4 * mm
while y > y0:
    c.line(x0, y, x1, y)
    y -= 6.5 * mm
c.showPage()

# 11 · savings tracker
base_page(c)
c.bookmarkPage("sec-track")
rail(c, 5)
header(c, "Savings pots", "Name each pot, set the goal, fill a cell each time you add to it")
x0, x1, y0, y1 = content_box()
pw = (x1 - x0 - 4 * mm) / 2
ph = (y1 - y0 - 8 * mm) / 3
for i in range(6):
    px = x0 + (i % 2) * (pw + 4 * mm)
    py = y1 - 2 * mm - (i // 2 + 1) * ph - (i // 2) * 4 * mm + 2 * mm
    c.setStrokeColor(FAINT); c.setLineWidth(0.7)
    c.roundRect(px, py, pw, ph - 2 * mm, 1.5 * mm, stroke=1, fill=0)
    c.setFillColor(SOFT); c.setFont("Helvetica", 6)
    c.drawString(px + 2.5 * mm, py + ph - 7.5 * mm, "POT ______________   GOAL ______")
    cells, ccols = 20, 10
    cell = (pw - 5 * mm) / ccols
    for j in range(cells):
        cx = px + 2.5 * mm + (j % ccols) * cell
        cyy = py + ph - 12 * mm - (j // ccols) * (cell + 0.8 * mm) - cell
        c.setStrokeColor(SOFT); c.setLineWidth(0.5)
        c.rect(cx, cyy, cell - 0.8 * mm, cell, stroke=1, fill=0)
    c.setFillColor(SOFT); c.setFont("Helvetica", 5.2)
    c.drawString(px + 2.5 * mm, py + 8.5 * mm, "NOTES / AMOUNTS")
    c.setStrokeColor(FAINT); c.setLineWidth(0.5)
    c.line(px + 2.5 * mm, py + 5.5 * mm, px + pw - 2.5 * mm, py + 5.5 * mm)
    c.line(px + 2.5 * mm, py + 2.5 * mm, px + pw - 2.5 * mm, py + 2.5 * mm)
c.showPage()

# 12 · habit tracker
base_page(c)
rail(c, 5)
header(c, "Habits", "One row per habit, one column per day")
x0, x1, y0, y1 = content_box()
label_w = 26 * mm
ncols, nrows = 31, 12
gw = (x1 - x0 - label_w) / ncols
gh = (y1 - y0 - 8 * mm) / nrows
c.setFont("Helvetica", 4.4); c.setFillColor(SOFT)
for d in range(ncols):
    c.drawCentredString(x0 + label_w + gw * (d + 0.5), y1 - 4 * mm, str(d + 1))
c.setStrokeColor(FAINT); c.setLineWidth(0.4)
gtop = y1 - 5.5 * mm
for r in range(nrows + 1):
    c.line(x0, gtop - r * gh, x1, gtop - r * gh)
for col in range(ncols + 1):
    c.line(x0 + label_w + col * gw, gtop, x0 + label_w + col * gw, gtop - nrows * gh)
c.showPage()

# 13 · print & punch guide + about
base_page(c)
rail(c, -1)
header(c, "Printing & filing", "For ring-binder users")
x0, x1, y0, y1 = content_box()
guide = [
    "Print at 100% scale (no 'fit to page') on A5 paper, or two-up on A4 and cut down the middle.",
    "Every page keeps a 13 mm inner margin clear, so it can be punched for any A5 ring or disc system.",
    "Align your punch to the paper edge, not to printed marks: binders differ, your punch knows best.",
    "Left-handed pages: print the mirrored versions and file them facing the opposite direction.",
    "",
    "About this file: an original Leafline design. Personal use licence; not for resale or redistribution.",
    "PROTOTYPE v0.1 - internal costing build.",
]
y = y1 - 6 * mm
c.setFillColor(INK)
for g in guide:
    c.setFont("Helvetica", 7.8)
    words, line = g.split(), ""
    if not g:
        y -= 4 * mm
        continue
    for w_ in words:
        if c.stringWidth(line + " " + w_, "Helvetica", 7.8) > (x1 - x0):
            c.drawString(x0, y, line.strip()); y -= 4 * mm; line = w_
        else:
            line += " " + w_
    c.drawString(x0, y, line.strip()); y -= 6 * mm
wordmark(c, x0, y0 + 4 * mm, 11)
c.showPage()

c.save()
print(f"wrote {OUT}")
