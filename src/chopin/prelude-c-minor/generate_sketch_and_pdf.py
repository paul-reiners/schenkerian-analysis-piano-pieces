import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os

# ====== CONFIG ======
PDF_PATH = "chopin_schenkerian_sketch.pdf"
SKETCH_PNG = "chopin_schenkerian_sketch.png"
SCORE_IMAGE = "prelude_c_minor_score.png"   # <- put your score image here (PNG/JPG)
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

# ====== STEP 2: Build a twopage PDF (page 1: sketch+notes, page 2: score) ======
styles = getSampleStyleSheet()
doc = SimpleDocTemplate(PDF_PATH, pagesize=letter,
                        leftMargin=MARGIN, rightMargin=MARGIN,
                        topMargin=MARGIN, bottomMargin=MARGIN)
story = []

# ----- Page 1: Title + Notes + Sketch -----
story.append(Paragraph("<b>Schenkerian Sketch  Chopin, Prelude in C minor (Op. 28 No. 20)</b>", styles["Title"]))
story.append(Spacer(1, 12))

description = """
This sketch illustrates the structural levels in Chopins Prelude in C minor, Op. 28 No. 20.

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

# Fit sketch image within margins
story.append(Image(SKETCH_PNG, width=MAX_IMG_W, height=MAX_IMG_H * 0.55))  # 55% height to keep page airy

# Page break
story.append(PageBreak())

# ----- Page 2: Score excerpt -----
story.append(Paragraph("<b>Score Excerpt (Public Domain)</b>", styles["Heading1"]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Frédéric Chopin, Prelude in C minor, Op. 28 No. 20  first page excerpt. "
    "Used here from a public-domain source (e.g., IMSLP).", styles["Normal"]))
story.append(Spacer(1, 12))

if os.path.exists(SCORE_IMAGE):
    # Place the score image scaled to fit page content area
    # Use keepAspectRatio=True and let it scale to fit within bounds
    img = Image(SCORE_IMAGE)
    img.drawWidth = MAX_IMG_W
    img.drawHeight = MAX_IMG_H * 0.85  # Use 85% of max height to ensure it fits
    img._restrictSize(MAX_IMG_W, MAX_IMG_H * 0.85)
    story.append(img)
else:
    story.append(Paragraph(
        f"<i>(Score image not found at '{SCORE_IMAGE}'. "
        f"Export a 300dpi PNG/JPG of the first page and save it with that name.)</i>",
        styles["Italic"]))
    story.append(Spacer(1, 12))

doc.build(story)
print(f"Built twopage PDF: {PDF_PATH}")
