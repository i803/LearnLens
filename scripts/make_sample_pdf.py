"""Generate a deliberately synthetic, privacy-safe classroom demonstration worksheet."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "web" / "public" / "sample_math_test.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Hero", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=21, leading=25, textColor=colors.HexColor("#103c3b"), alignment=TA_CENTER, spaceAfter=8))
styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=9, leading=13, textColor=colors.HexColor("#61746e"), alignment=TA_CENTER))
styles.add(ParagraphStyle(name="Question", parent=styles["Heading3"], fontSize=11, leading=15, textColor=colors.HexColor("#183e3c"), spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle(name="Answer", parent=styles["BodyText"], fontSize=9.5, leading=14, leftIndent=10, textColor=colors.HexColor("#345b54")))
styles.add(ParagraphStyle(name="Feedback", parent=styles["BodyText"], fontSize=9, leading=13, leftIndent=10, textColor=colors.HexColor("#a4473a")))
styles.add(ParagraphStyle(name="Tiny", parent=styles["Normal"], fontSize=8, leading=11, textColor=colors.HexColor("#758580")))


def footer(canvas, doc):
    canvas.saveState()
    w, h = letter
    canvas.setFillColor(colors.HexColor("#a4473a"))
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(w/2, 0.34*inch, "SYNTHETIC DEMO - NOT A REAL STUDENT SUBMISSION")
    canvas.setFillColor(colors.HexColor("#82908b"))
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w-0.55*inch, 0.34*inch, f"Page {doc.page}")
    canvas.restoreState()

story = [
    Paragraph("Foundation Mathematics: Sets", styles["Hero"]),
    Paragraph("Sample marked worksheet for LearnLens AI's hackathon demonstration", styles["Sub"]),
    Spacer(1, 12),
    Table([[Paragraph("DEMO DATA ONLY", ParagraphStyle("demo", parent=styles["Normal"], textColor=colors.white, fontName="Helvetica-Bold", alignment=TA_CENTER, fontSize=10)),
            Paragraph("Every name and answer is invented. Do not present as real student evidence.", ParagraphStyle("demotext", parent=styles["Normal"], textColor=colors.white, fontSize=9))]], colWidths=[1.55*inch, 4.75*inch], style=TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#a4473a")), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("LEFTPADDING", (0,0), (-1,-1), 9), ("RIGHTPADDING", (0,0), (-1,-1), 9),
                ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 8)])),
    Spacer(1, 10),
    Paragraph("Instructions", styles["Heading2"]),
    Paragraph("Answer each question briefly. The answer samples and teacher comments below are authored only to exercise the software flow.", styles["BodyText"]),
    Spacer(1, 4),
]
questions = [
    ("1. Set-builder notation (2 marks)", "Write B = {3, 9, 27, 81} in set-builder form.", "B = {3, 9, 27, 81}", "This repeats the roster form. One valid set-builder form is B = {3^n : n is a natural number and 1 <= n <= 4}.", 1, 2),
    ("2. Empty set (1 mark)", "Is A = {x in N : 3 < x < 4} empty?", "A is not empty.", "No natural number lies strictly between 3 and 4, so A is empty.", 0, 1),
    ("3. Finite or infinite (2 marks)", "Is the set of all points on a circle's circumference finite or infinite? Give a reason.", "Finite.", "A circle's circumference contains infinitely many points, so the set is infinite.", 0, 2),
    ("4. Equal sets (2 marks)", "Are A = {-2, 2} and B = {x in Z : x^2 = 4} equal? Why?", "No.", "Yes. The integer solutions of x^2 = 4 are -2 and 2, so B = {-2, 2} and both sets are equal.", 0, 2),
    ("5. Interval notation (2 marks)", "Write (-5, 9] in set-builder form.", "{x : -5 < x < 9}", "The right endpoint 9 is included, so the condition must be -5 < x and x <= 9.", 1, 2),
    ("6. Set operations (3 marks)", "If A = [-3, 5] and B = (0, 6], find A - B and A union B.", "A - B = (-3, 0] and A union B = (-3, 6)", "0 is not in B, so 0 remains in A - B. The value -3 belongs to A and 6 belongs to B, so A union B includes both endpoints: [-3, 6]. Also, -3 must remain included in A - B.", 1, 3),
    ("7. Disjoint sets (1 mark)", "Are A = {1, 2, 3, 4} and B = {x in N : 5 <= x <= 7} disjoint?", "No, they share values.", "They have no common elements: A contains 1 to 4 and B contains 5, 6 and 7. The sets are disjoint.", 0, 1),
    ("8. Cardinality (2 marks)", "If n(X)=19, n(Y)=37, and n(X intersection Y)=12, find n(X union Y).", "68", "Use n(X union Y) = n(X) + n(Y) - n(X intersection Y) = 19 + 37 - 12 = 44.", 0, 2)
]
awarded_total = sum(q[4] for q in questions)
possible_total = sum(q[5] for q in questions)
for idx, (heading, prompt, answer, feedback, awarded, possible) in enumerate(questions):
    block = [
        Paragraph(heading, styles["Question"]),
        Paragraph(prompt, styles["BodyText"]),
        Spacer(1, 3),
        Paragraph(f"<b>Sample response:</b> {answer}", styles["Answer"]),
        Paragraph(f"<b>Illustrative marks:</b> {awarded} / {possible}", styles["Tiny"]),
        Paragraph(f"<b>Teacher feedback:</b> {feedback}", styles["Feedback"]),
        Spacer(1, 5),
    ]
    story.append(KeepTogether(block))
    if idx == 3:
        story.append(PageBreak())
        story.extend([Paragraph("Marked response examples (continued)", styles["Heading2"]), Paragraph("These comments are demonstration annotations, not a real teacher marking record.", styles["Tiny"]), Spacer(1, 8)])
story.extend([Spacer(1, 6), Table([[Paragraph("Total shown on the sample record", styles["BodyText"]), Paragraph(f"{awarded_total} / {possible_total} marks (illustrative only)", styles["BodyText"]) ]], colWidths=[3.3*inch, 3.0*inch], style=TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#edf5ef")),("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#dbe4dc")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)])), Spacer(1, 8), Paragraph("For responsible demonstrations", styles["Heading2"]), Paragraph("This PDF is synthetic test data. Do not claim it represents a real learner, a measured accuracy benchmark, or pilot evidence. Human review is required before any educational judgement.", styles["BodyText"])])

doc = SimpleDocTemplate(str(OUT), pagesize=letter, rightMargin=0.6*inch, leftMargin=0.6*inch, topMargin=0.55*inch, bottomMargin=0.62*inch, title="Synthetic LearnLens Demo Worksheet", author="LearnLens team")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
