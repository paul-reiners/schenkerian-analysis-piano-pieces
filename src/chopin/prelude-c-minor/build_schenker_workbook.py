# build_schenker_workbook.py
import os, io, textwrap, requests, tempfile
from pathlib import Path
from pdf2image import convert_from_bytes
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                PageBreak, Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image as PILImage

# ----------------------------
# CONFIG: repertoire sources (all public-domain or CC-BY-SA typesets)
# ----------------------------
SOURCES = {
    # Bach chorale (BWV 269)  Mutopia (Public Domain)
    "bach_chorale_bwv269": {
        "title": "Bach: Chorale (BWV 269)  Aus meines Herzens Grunde",
        "url": "https://www.mutopiaproject.org/ftp/BachJS/BWV269/bwv_269/bwv_269-a4.pdf",
        "license": "Public Domain (Mutopia typeset)",
        "citation": "Mutopia BWV 269 (Public Domain).",
        "page": 1
    },
    # Bach Invention No. 1 in C, BWV 772  Mutopia (CC-BY-SA or PD depending edition; this file is CC-BY-SA)
    "bach_invention_bwv772": {
        "title": "Bach: Invention No. 1 in C, BWV 772 (mm. 14 focus)",
        "url": "https://www.mutopiaproject.org/ftp/BachJS/BWV772/bach-invention-01/bach-invention-01-a4.pdf",
        "license": "CC BY-SA 3.0 (Mutopia typeset)  include attribution",
        "citation": "Mutopia BWV 772 (CC BY-SA 3.0).",
        "page": 1
    },
    # Mozart K.545 (Allegro)  Mutopia (public typeset)
    "mozart_k545": {
        "title": "Mozart: Sonata K.545 I (cadential study)",
        "url": "https://www.mutopiaproject.org/ftp/MozartWA/KV545/K545-1/K545-1-let.pdf",
        "license": "Mutopia typeset (license noted on score)",
        "citation": "Mutopia Mozart K.545-1 (see score for license).",
        "page": 1
    },
    # Chopin Prelude Op.28 No.20  Mutopia (Public Domain typeset)
    "chopin_op28_20": {
        "title": "Chopin: Prelude in C minor, Op. 28 No. 20",
        "url": "https://www.mutopiaproject.org/ftp/ChopinFF/O28/Chop-28-20/Chop-28-20-a4.pdf",
        "license": "Public Domain (Mutopia typeset)",
        "citation": "Mutopia Chopin Op.28/20 (Public Domain).",
        "page": 1
    },
}

# ----------------------------
# HELPERS
# ----------------------------
def fetch_pdf(url: str) -> bytes:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.content

def pdf_page_to_png(pdf_bytes: bytes, page_number: int, dpi=300) -> PILImage.Image:
    # page_number is 1-based
    imgs = convert_from_bytes(pdf_bytes, dpi=dpi, first_page=page_number, last_page=page_number)
    return imgs[0]

def caption(s: str) -> Paragraph:
    return Paragraph(s, styles["Normal"])

def h1(s: str): return Paragraph(f"<b>{s}</b>", styles["Heading1"])
def h2(s: str): return Paragraph(f"<b>{s}</b>", styles["Heading2"])
def h3(s: str): return Paragraph(f"<b>{s}</b>", styles["Heading3"])

def hr(sp=6):
    tbl = Table([[""]], colWidths=[PAGE_W-2*MARGIN], rowHeights=[0.4])
    tbl.setStyle(TableStyle([("LINEBELOW", (0,0), (-1,-1), 0.6, colors.grey)]))
    return [tbl, Spacer(1, sp)]

# ----------------------------
# OUTPUT DOC
# ----------------------------
PAGE_W, PAGE_H = letter
MARGIN = 0.75 * inch
styles = getSampleStyleSheet()

OUT = Path("Schenkerian_Analysis_Workbook.pdf")
doc = SimpleDocTemplate(
    str(OUT), pagesize=letter,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=MARGIN
)

story = []

# ----------------------------
# FRONT MATTER
# ----------------------------
story += [
    Paragraph("<b>Schenkerian Analysis Workbook</b>", styles["Title"]),
    Spacer(1, 8),
    Paragraph("12-Week Self-Study · Public-Domain Excerpts Included", styles["Italic"]),
    Spacer(1, 18),
    caption("This workbook guides you from foreground reductions to middleground and background sketches, with short public-domain excerpts embedded for hands-on practice."),
    Spacer(1, 18),
]
story += hr()
story += [h2("How to Use"), caption(
    "1) For each excerpt, first reduce to soprano + bass; 2) identify the Urlinie (321 or 54321); "
    "3) outline the bass arpeggiation (IVI); 4) mark prolongations and cadential patterns."
)]
story.append(PageBreak())

# ----------------------------
# STUDY PLAN (CONDENSED)
# ----------------------------
story += [h1("12-Week Study Plan (Condensed)")]
plan_points = [
    ("Weeks 12", "Foundations: Urlinie, Bassbrechung, simple reductions (Bach chorales)."),
    ("Weeks 34", "Foreground reductions: Bach inventions (24 bar segments)."),
    ("Weeks 56", "Middleground: prolongations across phrases; neighbor/passing harmonies."),
    ("Weeks 78", "Cadences & dominant prolongations: Mozart K.545 (Allegro)."),
    ("Weeks 910", "Small complete works: Chopin preludes."),
    ("Weeks 1112", "Integration: complete background sketch; written commentary."),
]
table = Table(
    [["Week(s)", "Focus"]] + plan_points,
    colWidths=[1.4*inch, (PAGE_W-2*MARGIN) - 1.4*inch]
)
table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BOX", (0,0), (-1,-1), 0.75, colors.black)
]))
story += [table, Spacer(1, 12)]
story += [caption("Tip: play reductions at the keyboard to internalize the hierarchy."), PageBreak()]

# ----------------------------
# DOWNLOAD & RENDER EXCERPTS
# ----------------------------
tmpdir = Path(tempfile.mkdtemp())
images = {}  # key -> PNG path
for key, meta in SOURCES.items():
    pdf_bytes = fetch_pdf(meta["url"])
    img = pdf_page_to_png(pdf_bytes, meta["page"], dpi=300)
    out_png = tmpdir / f"{key}.png"
    img.save(out_png)
    images[key] = out_png

# ----------------------------
# WEEKLY SECTIONS WITH EXCERPTS + STAFF SPACE
# ----------------------------
def exercise_page(title, prompt, key, height_scale=0.45):
    story.append(h2(title))
    story.append(Spacer(1, 6))
    story.append(caption(prompt))
    story.append(Spacer(1, 8))
    img_path = images[key]
    # Scale to fit page
    max_w = PAGE_W - 2*MARGIN
    max_h = (PAGE_H - 2*MARGIN) * height_scale
    story.append(Image(str(img_path), width=max_w, height=max_h))
    story.append(Spacer(1, 6))
    story.append(caption("<i>Source:</i> " + SOURCES[key]["citation"]))
    story.append(caption("<i>License:</i> " + SOURCES[key]["license"]))
    story.append(Spacer(1, 10))
    # Add a few blank staff lines (simple lines as placeholders)
    staff_rows = 8
    row = Table([[" "]] * staff_rows, colWidths=[max_w], rowHeights=[0.35*inch]*staff_rows)
    row.setStyle(TableStyle([
        ("LINEABOVE", (0,0), (-1,0), 0.8, colors.black),
        ("LINEABOVE", (0,1), (-1,1), 0.8, colors.black),
        ("LINEABOVE", (0,2), (-1,2), 0.8, colors.black),
        ("LINEABOVE", (0,3), (-1,3), 0.8, colors.black),
        ("LINEABOVE", (0,4), (-1,4), 0.8, colors.black),
        ("LINEABOVE", (0,5), (-1,5), 0.8, colors.black),
        ("LINEABOVE", (0,6), (-1,6), 0.8, colors.black),
        ("LINEABOVE", (0,7), (-1,7), 0.8, colors.black),
    ]))
    story.append(row)
    story.append(PageBreak())

# Weeks 12: Bach Chorale
exercise_page(
    "Weeks 12 · Bach Chorale (BWV 269)",
    "Reduce to soprano + bass; propose an Urlinie (likely 321) and outline IVI bass. "
    "Mark passing/neighbor tones; notate a cadential 64 if present.",
    "bach_chorale_bwv269"
)

# Weeks 34: Bach Invention (foreground)
exercise_page(
    "Weeks 34 · Bach Invention in C, BWV 772 (mm. 14 focus)",
    "Foreground reduction: remove surface figuration; keep structural tones. Identify basic soprano line and bass support. "
    "Circle passing tones; beam an Urlinie if applicable.",
    "bach_invention_bwv772"
)

# Weeks 78: Mozart K.545 (cadences)
exercise_page(
    "Weeks 78 · Mozart K.545 I (cadential patterns)",
    "Locate cadential 64, dominant prolongations, and resolution. Sketch soprano descent over VI.",
    "mozart_k545"
)

# Weeks 910: Chopin Prelude (middleground)
exercise_page(
    "Weeks 910 · Chopin, Prelude in C minor, Op.28/20",
    "Identify Urlinie (321) and IVI bass arpeggiation. Mark mIII and N6 as predominant intensifiers toward V.",
    "chopin_op28_20",
    height_scale=0.52
)

# ----------------------------
# REFERENCE PAGES
# ----------------------------
story += [h1("Reference: Urlinie & Bass Archetypes"), Spacer(1,8)]
ref_tbl = Table([
    ["Urlinie Types", "Bass Archetypes"],
    ["321 · 54321", "IVI · IIVVI"],
    ["Tips", "Tips"],
    ["Beam only structural steps across phrases.", "Treat IV/ii/N6 as predominant prolongations."]
], colWidths=[(PAGE_W-2*MARGIN)/2]*2)
ref_tbl.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BOX", (0,0), (-1,-1), 0.75, colors.black)
]))
story += [ref_tbl, Spacer(1,12)]
story += [h2("Cadential Patterns"), caption("Cadential 64  V  I · vii°/V  V · N6  V.")]
story += [Spacer(1,6)]
story += hr()[0:1]
story += [PageBreak()]

# ----------------------------
# LEGENDS & HARMONIC OUTLINE TEMPLATE
# ----------------------------
story += [h1("Legends & Quick Glossary"), Spacer(1,8)]
legend_text = """
<b>N6</b> = Neapolitan sixth (mII in 1st inversion).<br/>
<b>vii°/V</b> = Leading-tone diminished triad to dominant.<br/>
<b>Cadential 64</b> = I64 over V resolving to V.<br/>
<b>T/S/D</b> = Tonic / Subdominant (Predominant) / Dominant (German functional labels).<br/>
<b>Prolongation</b> = Extending a harmony across time via voice-leading (passing/neighbor chords).<br/>
"""
story += [Paragraph(legend_text, styles["Normal"]), PageBreak()]

# ----------------------------
# PROGRESS TRACKER
# ----------------------------
story += [h1("Progress Tracker"), Spacer(1,8)]
tracker = Table(
    [["Date", "Piece", "Urlinie", "Bass (IVI?)", "Observations"]] +
    [["", "", "", "", ""] for _ in range(14)],
    colWidths=[0.9*inch, 2.0*inch, 1.2*inch, 1.2*inch, (PAGE_W-2*MARGIN) - (0.9+2.0+1.2+1.2)*inch]
)
tracker.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BOX", (0,0), (-1,-1), 0.75, colors.black)
]))
story += [tracker, PageBreak()]

# ----------------------------
# BUILD
# ----------------------------
doc.build(story)
print(f"Built: {OUT.resolve()}")
