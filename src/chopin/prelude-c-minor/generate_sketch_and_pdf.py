import matplotlib.pyplot as plt
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

# ====== CONFIG ======
PDF_PATH = "chopin_schenkerian_sketch.pdf"
SKETCH_PNG = "chopin_schenkerian_sketch.png"
SCORE_IMAGE = "prelude_c_minor_score.png"  # <- put your score image here (PNG/JPG)
PAGE_W, PAGE_H = letter
MARGIN = 0.75 * inch
MAX_IMG_W = PAGE_W - 2 * MARGIN
MAX_IMG_H = PAGE_H - 2 * MARGIN

# ====== STEP 1: Create the annotated Schenkerian sketch image ======
fig, ax = plt.subplots(figsize=(11, 6))

# Urlinie (321)
x = [1, 5, 9]
y = [3, 2, 1]
labels = ["Em (3)\n(mm.14)", "D (2)\n(mm.810)", "C (1)\n(mm.1113)"]
ax.plot(x, y, marker="o", linewidth=2)
for i, label in enumerate(labels):
    ax.text(x[i], y[i] + 0.2, label, ha="center", fontsize=11)

# Bass with expansions
bass_x = [1, 3, 4, 5, 7, 9]
bass_y = [-1, -0.5, -0.7, -2, -1.5, -1]
bass_labels = [
    "C (I)\n(mm.12)",
    "Em (mIII)\n(m.5)",
    "dim passing\n(m.6)",
    "G (V)\n(mm.78)",
    "N6 (Dm)\n(m.9)",
    "C (I)\n(mm.1113)"
]
ax.plot(bass_x, bass_y, marker="o", linewidth=2)
for i, label in enumerate(bass_labels):
    ax.text(bass_x[i], bass_y[i] - 0.3, label, ha="center", fontsize=9)

# Connect Urlinie to bass
for ux, uy, bx, by in zip([1, 5, 9], [3, 2, 1], [1, 5, 9], [-1, -2, -1]):
    ax.plot([ux, bx], [uy, by], linestyle="dotted")

ax.set_ylim(-3, 4)
ax.set_xlim(0, 10)
ax.axis("off")
ax.set_title("Schenkerian Sketch with Measure References  Chopin, Prelude in C minor (Op. 28 No. 20)", fontsize=13)

plt.savefig(SKETCH_PNG, dpi=300, bbox_inches="tight")
plt.close()

# ====== STEP 2: Build the PDF ======
styles = getSampleStyleSheet()
doc = SimpleDocTemplate(
    PDF_PATH, pagesize=letter,
    leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN
)
story = []

# ---------- PAGE 1: Sketch + Notes ----------
story.append(Paragraph("<b>Schenkerian Sketch  Chopin, Prelude in C minor (Op. 28 No. 20)</b>", styles["Title"]))
story.append(Spacer(1, 12))

description = """
This sketch illustrates structural levels in Chopins Prelude in C minor, Op. 28 No. 20.

<b>Urlinie (321):</b>
- Em (3), prolonged in mm. 14
- D (2), emphasized in mm. 810 (cadential area)
- C (1), resolution in mm. 1113

<b>Bass Arpeggiation (IVI), with expansions:</b>
- C (I), mm. 12
- Em (mIII), m. 5
- Diminished passing harmony, m. 6
- G (V), mm. 78
- N6 (Dm), m. 9 (dominant intensification)
- C (I), mm. 1113

This shows how Chopin dramatizes a simple IVI framework with rich harmonic intensifications.
"""
story.append(Paragraph(description, styles["Normal"]))
story.append(Spacer(1, 18))
story.append(Image(SKETCH_PNG, width=MAX_IMG_W, height=MAX_IMG_H * 0.55))
story.append(PageBreak())

# ---------- PAGE 2: Score Excerpt ----------
story.append(Paragraph("<b>Score Excerpt (Public Domain)</b>", styles["Heading1"]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Frédéric Chopin, Prelude in C minor, Op. 28 No. 20  first page excerpt. "
    "Public domain source (e.g., IMSLP).", styles["Normal"]
))
story.append(Spacer(1, 12))

if os.path.exists(SCORE_IMAGE):
    # Scale image to fit within page bounds while maintaining aspect ratio
    img = Image(SCORE_IMAGE)
    img._restrictSize(MAX_IMG_W, MAX_IMG_H * 0.85)
    story.append(img)
else:
    story.append(Paragraph(
        f"<i>(Score image not found at '{SCORE_IMAGE}'. "
        f"Export a 300-dpi PNG/JPG of the first page and save it with that name.)</i>",
        styles["Italic"]))
    story.append(Spacer(1, 12))

story.append(PageBreak())

# ---------- PAGE 3: Roman-Numeral Harmonic Outline ----------
story.append(Paragraph("<b>Harmonic Outline (Roman Numerals by Measure)</b>", styles["Heading1"]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Compact harmonic roadmap in C minor. Local spellings/voicings vary by edition; "
    "outline reflects a common reading aligned with the Schenkerian middleground.",
    styles["Normal"]))
story.append(Spacer(1, 12))

# Table data: [Measure(s), Harmony (Roman numerals), Function / Notes]
data = [
    ["mm. 12",  "i",                 "Tonic, initial statement / prolongation"],
    ["mm. 34",  "i (prolonged)",     "Continuation of tonic support"],
    ["m.  5",    "mIII",              "Upper-third expansion of I (Em major)"],
    ["m.  6",    "vii°/V (passing)",  "Leading-tone diminished harmony to V"],
    ["mm. 78",  "V (prolonged)",     "Dominant preparation"],
    ["m.  9",    "N6  V",            "Neapolitan (Dm) intensifies the dominant"],
    ["m. 10",    "V (cadential)",     "Dominant close; prepares resolution"],
    ["mm. 1113","i",                 "Tonic resolution / close"],
]

table = Table(data, colWidths=[1.2*inch, 1.5*inch, MAX_IMG_W - (1.2*inch + 1.5*inch)])
table.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("ALIGN", (0,0), (-1,0), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BOX", (0,0), (-1,-1), 0.75, colors.black),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
]))
# Add a header row label
data.insert(0, ["Measure(s)", "Harmony", "Function / Notes"])
# Rebuild table with header formatting
table = Table(data, colWidths=[1.2*inch, 1.5*inch, MAX_IMG_W - (1.2*inch + 1.5*inch)])
table.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("ALIGN", (0,0), (-1,0), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BOX", (0,0), (-1,-1), 0.75, colors.black),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
]))

story.append(table)
story.append(Spacer(1, 10))
story.append(Paragraph(
    "<i>Notes:</i> The N6 (Dm) functions as an intensified predominant that resolves to V; "
    "the diminished harmony in m. 6 is read as vii° of the dominant (a passing dominant-preparation). "
    "Foreground variants may label cadential 64 in the V area; the middleground here rolls it into the V prolongation.",
    styles["Normal"]))

# Build PDF
doc.build(story)
print(f"Built three-page PDF: {PDF_PATH}")
