"""
PhysioAssist PDF Generator v2
- Full detailed report (PDF 1)
- Quick Reference Card (PDF 2)
- Clickable links, professional formatting
"""

import re
from io import BytesIO


def _safe_html(text: str) -> str:
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def _make_doc(buf, title="PhysioAssist Report"):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate

    return SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=2.2*cm, leftMargin=2.2*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
        title=title, author="PhysioAssist"
    )


def _make_styles():
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_LEFT, TA_CENTER

    BLUE   = HexColor("#1565C0")
    GREEN  = HexColor("#2E7D32")
    RED    = HexColor("#C62828")
    DARK   = HexColor("#212121")
    GRAY   = HexColor("#616161")
    LIGHT  = HexColor("#E3F2FD")
    DIVIDER= HexColor("#BDBDBD")

    return {
        "title": ParagraphStyle("title", fontName="Helvetica-Bold",
            fontSize=22, textColor=BLUE, leading=28, spaceAfter=2),
        "subtitle": ParagraphStyle("subtitle", fontName="Helvetica",
            fontSize=11, textColor=GRAY, leading=16, spaceAfter=14),
        "section": ParagraphStyle("section", fontName="Helvetica-Bold",
            fontSize=13, textColor=BLUE, leading=18, spaceBefore=14, spaceAfter=6),
        "exercise_title": ParagraphStyle("ex_title", fontName="Helvetica-Bold",
            fontSize=12, textColor=GREEN, leading=16, spaceBefore=12, spaceAfter=4),
        "body": ParagraphStyle("body", fontName="Helvetica",
            fontSize=10.5, textColor=DARK, leading=16, spaceBefore=2, spaceAfter=2),
        "bold_body": ParagraphStyle("bold_body", fontName="Helvetica-Bold",
            fontSize=10.5, textColor=DARK, leading=16, spaceBefore=3, spaceAfter=2),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica",
            fontSize=10.5, textColor=DARK, leading=15,
            leftIndent=14, spaceBefore=1, spaceAfter=1),
        "warning": ParagraphStyle("warning", fontName="Helvetica-Bold",
            fontSize=10, textColor=RED, leading=14, spaceBefore=4, spaceAfter=4),
        "link": ParagraphStyle("link", fontName="Helvetica",
            fontSize=10, textColor=BLUE, leading=14, spaceBefore=2, spaceAfter=2),
        "disclaimer": ParagraphStyle("disclaimer", fontName="Helvetica-Oblique",
            fontSize=9, textColor=GRAY, leading=13, spaceBefore=6),
        # Quick card styles
        "card_title": ParagraphStyle("card_title", fontName="Helvetica-Bold",
            fontSize=18, textColor=BLUE, leading=24, spaceAfter=4, alignment=TA_CENTER),
        "card_section": ParagraphStyle("card_section", fontName="Helvetica-Bold",
            fontSize=11, textColor=GREEN, leading=15, spaceBefore=10, spaceAfter=4),
        "card_body": ParagraphStyle("card_body", fontName="Helvetica",
            fontSize=10, textColor=DARK, leading=14, spaceBefore=1, spaceAfter=1),
        "card_bullet": ParagraphStyle("card_bullet", fontName="Helvetica",
            fontSize=10, textColor=DARK, leading=14,
            leftIndent=12, spaceBefore=1, spaceAfter=1),
    }


def _add_links(text: str) -> str:
    """Make URLs clickable in ReportLab paragraphs."""
    url_re = r'(https?://[^\s\)\]<>]+)'
    def replace(m):
        url = m.group(1)
        display = url if len(url) <= 60 else url[:57] + "..."
        return f'<link href="{url}"><u>{_safe_html(display)}</u></link>'
    return re.sub(url_re, replace, _safe_html(text))


def _parse_report(report_text: str, styles: dict, full: bool = True):
    """Parse report text into ReportLab flowables."""
    from reportlab.platypus import Paragraph, Spacer, HRFlowable
    from reportlab.lib.colors import HexColor
    from reportlab.lib.units import cm

    DIVIDER = HexColor("#BDBDBD")
    story = []

    for line in report_text.split("\n"):
        line = line.rstrip()

        if not line:
            story.append(Spacer(1, 0.12*cm))
            continue

        # Section header ===
        if line.startswith("===") and line.endswith("==="):
            txt = line.strip("=").strip()
            story.append(HRFlowable(width="100%", thickness=0.5,
                color=DIVIDER, spaceBefore=8, spaceAfter=4))
            story.append(Paragraph(_safe_html(txt),
                styles["section"] if full else styles["card_section"]))
            continue

        # Section header ###
        if line.startswith("###"):
            txt = line.replace("#", "").strip()
            story.append(Paragraph(_safe_html(txt),
                styles["section"] if full else styles["card_section"]))
            continue

        # Exercise title
        if re.match(r'^EXERCISE\s+\d+:', line, re.IGNORECASE):
            story.append(Paragraph(_safe_html(line),
                styles["exercise_title"]))
            continue

        # Warning
        if line.upper().startswith("WARNING:") or "RED FLAG" in line.upper():
            story.append(Paragraph(f"\u26a0 {_add_links(line)}",
                styles["warning"]))
            continue

        # URL line
        if "youtube.com" in line.lower() or "youtu.be" in line.lower():
            story.append(Paragraph(_add_links(line), styles["link"]))
            continue

        if "profphysio.com" in line.lower() or "amazon.com" in line.lower():
            story.append(Paragraph(_add_links(line), styles["link"]))
            continue

        # Bullet
        if line.startswith("- ") or line.startswith("* "):
            content = _add_links(line[2:])
            story.append(Paragraph(f"\u2022 {content}",
                styles["bullet"] if full else styles["card_bullet"]))
            continue

        # Numbered
        if re.match(r'^\s*\d+\.', line):
            story.append(Paragraph(_add_links(line),
                styles["bullet"] if full else styles["card_bullet"]))
            continue

        # Key: value
        if ":" in line and len(line) < 120 and not line.startswith("http"):
            parts = line.split(":", 1)
            key = _safe_html(parts[0].strip())
            val = _add_links(parts[1].strip()) if len(parts) > 1 else ""
            if val:
                story.append(Paragraph(
                    f"<b>{key}:</b> {val}",
                    styles["body"] if full else styles["card_body"]))
            else:
                story.append(Paragraph(
                    f"<b>{_add_links(line)}</b>",
                    styles["bold_body"] if full else styles["card_body"]))
            continue

        # Default
        story.append(Paragraph(_add_links(line),
            styles["body"] if full else styles["card_body"]))

    return story


def generate_full_pdf(report_text: str, patient_name: str, lang: str = "en") -> bytes:
    """Generate detailed full report PDF."""
    try:
        from reportlab.platypus import Paragraph, Spacer, HRFlowable
        from reportlab.lib.colors import HexColor
        from reportlab.lib.units import cm

        buf = BytesIO()
        doc = _make_doc(buf, f"PhysioAssist Report - {patient_name}")
        styles = _make_styles()

        story = []

        # Header
        story.append(Paragraph("PhysioAssist", styles["title"]))
        story.append(Paragraph(
            f"Physical Therapy Assessment Report  |  {_safe_html(patient_name)}",
            styles["subtitle"]
        ))
        story.append(HRFlowable(width="100%", thickness=2,
            color=HexColor("#1565C0"), spaceAfter=16))

        # Report body
        story.extend(_parse_report(report_text, styles, full=True))

        # Disclaimer
        story.append(Spacer(1, 0.4*cm))
        story.append(HRFlowable(width="100%", thickness=0.5,
            color=HexColor("#BDBDBD"), spaceAfter=8))
        story.append(Paragraph(
            "This report is for educational purposes based on international PT protocols. "
            "Not a substitute for professional diagnosis. Consult a licensed physiotherapist. "
            "| PhysioAssist | As an Amazon Associate I earn from qualifying purchases.",
            styles["disclaimer"]
        ))

        doc.build(story)
        return buf.getvalue()

    except Exception as e:
        return f"PDF Error: {e}\n\n{report_text}".encode("utf-8")


def generate_quick_card_pdf(report_text: str, patient_name: str, lang: str = "en") -> bytes:
    """Generate compact quick-reference card PDF."""
    try:
        from reportlab.platypus import (Paragraph, Spacer, HRFlowable,
                                         Table, TableStyle)
        from reportlab.lib.colors import HexColor, white
        from reportlab.lib.units import cm

        buf = BytesIO()
        doc = _make_doc(buf, f"PhysioAssist Quick Card - {patient_name}")
        styles = _make_styles()

        # Extract key sections from report
        sections = _extract_quick_sections(report_text)

        story = []

        # Header
        story.append(Paragraph(
            "PhysioAssist \u2014 Quick Reference Card",
            styles["card_title"]
        ))
        story.append(Paragraph(
            f"Patient: {_safe_html(patient_name)}",
            styles["subtitle"]
        ))
        story.append(HRFlowable(width="100%", thickness=2,
            color=HexColor("#1565C0"), spaceAfter=12))

        # Diagnosis
        if sections.get("diagnosis"):
            story.append(Paragraph(
                "\U0001f3af Diagnosis" if lang == "en" else "\U0001f3af \u0627\u0644\u062a\u0634\u062e\u064a\u0635",
                styles["card_section"]
            ))
            story.append(Paragraph(
                _safe_html(sections["diagnosis"]), styles["card_body"]
            ))
            story.append(HRFlowable(width="100%", thickness=0.3,
                color=HexColor("#E0E0E0"), spaceAfter=4))

        # Exercises (brief)
        if sections.get("exercises"):
            label = "\U0001f3cb Your Exercises" if lang == "en" else "\U0001f3cb \u062a\u0645\u0627\u0631\u064a\u0646\u0643"
            story.append(Paragraph(label, styles["card_section"]))
            for ex in sections["exercises"][:4]:
                story.append(Paragraph(
                    f"\u2022 <b>{_safe_html(ex['name'])}</b>: {_safe_html(ex['dose'])}",
                    styles["card_bullet"]
                ))
                if ex.get("video"):
                    story.append(Paragraph(
                        f"  \U0001f3ac {_add_links(ex['video'])}",
                        styles["link"]
                    ))
            story.append(HRFlowable(width="100%", thickness=0.3,
                color=HexColor("#E0E0E0"), spaceAfter=4))

        # Physical therapy modalities
        if sections.get("modalities"):
            label = "\u2744\ufe0f\U0001f525 Home Physical Therapy" if lang == "en" else "\u2744\ufe0f\U0001f525 \u0637\u0628\u064a\u0639\u064a \u0645\u0646\u0632\u0644\u064a"
            story.append(Paragraph(label, styles["card_section"]))
            for item in sections["modalities"][:4]:
                story.append(Paragraph(
                    f"\u2022 {_safe_html(item)}", styles["card_bullet"]
                ))
            story.append(HRFlowable(width="100%", thickness=0.3,
                color=HexColor("#E0E0E0"), spaceAfter=4))

        # Key instructions
        if sections.get("instructions"):
            label = "\u2705 Key Instructions" if lang == "en" else "\u2705 \u062a\u0639\u0644\u064a\u0645\u0627\u062a \u0623\u0633\u0627\u0633\u064a\u0629"
            story.append(Paragraph(label, styles["card_section"]))
            for item in sections["instructions"][:5]:
                story.append(Paragraph(
                    f"\u2022 {_safe_html(item)}", styles["card_bullet"]
                ))
            story.append(HRFlowable(width="100%", thickness=0.3,
                color=HexColor("#E0E0E0"), spaceAfter=4))

        # Precautions
        if sections.get("precautions"):
            label = "\U0001f6ab Do NOT Do" if lang == "en" else "\U0001f6ab \u0645\u0648\u0627\u0646\u0639"
            story.append(Paragraph(label, styles["card_section"]))
            for item in sections["precautions"][:5]:
                story.append(Paragraph(
                    f"\u274c {_safe_html(item)}", styles["card_bullet"]
                ))

        # Footer
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width="100%", thickness=0.5,
            color=HexColor("#BDBDBD"), spaceAfter=6))
        story.append(Paragraph(
            "PhysioAssist | For educational purposes only. Consult a licensed physiotherapist.",
            styles["disclaimer"]
        ))

        doc.build(story)
        return buf.getvalue()

    except Exception as e:
        return f"Quick Card Error: {e}".encode("utf-8")


def _extract_quick_sections(report_text: str) -> dict:
    """Extract key sections from full report for quick card."""
    sections = {
        "diagnosis": "",
        "exercises": [],
        "modalities": [],
        "instructions": [],
        "precautions": [],
    }

    lines = report_text.split("\n")
    current_section = None
    current_exercise = None
    in_exercise = False

    for line in lines:
        line_strip = line.strip()

        # Detect sections
        if "DIAGNOSIS" in line_strip.upper() or "CLINICAL" in line_strip.upper():
            current_section = "diagnosis"
            continue
        elif "EXERCISE PROGRAM" in line_strip.upper() or "HOME EXERCISE" in line_strip.upper():
            current_section = "exercises"
            continue
        elif "THERMAL" in line_strip.upper() or "MODALI" in line_strip.upper() or "PHYSICAL THERAPY" in line_strip.upper():
            current_section = "modalities"
            continue
        elif "ACTIVITY MODIF" in line_strip.upper() or "DAILY" in line_strip.upper():
            current_section = "instructions"
            continue
        elif "CONTRAIND" in line_strip.upper() or "PRECAUTION" in line_strip.upper():
            current_section = "precautions"
            continue
        elif line_strip.startswith("===") or line_strip.startswith("###"):
            current_section = None
            in_exercise = False
            current_exercise = None
            continue

        if not line_strip:
            continue

        # Parse by section
        if current_section == "diagnosis" and not sections["diagnosis"]:
            if "Most likely" in line_strip or "diagnosis:" in line_strip.lower():
                sections["diagnosis"] = line_strip.split(":", 1)[-1].strip()

        elif current_section == "exercises":
            ex_match = re.match(r'^EXERCISE\s+(\d+):\s*(.+)', line_strip, re.IGNORECASE)
            if ex_match:
                current_exercise = {"name": ex_match.group(2), "dose": "", "video": ""}
                sections["exercises"].append(current_exercise)
                in_exercise = True
            elif current_exercise and in_exercise:
                if "Dose:" in line_strip or "sets" in line_strip.lower():
                    current_exercise["dose"] = line_strip.split(":", 1)[-1].strip()[:80]
                elif "youtube.com" in line_strip.lower() or "youtu.be" in line_strip.lower():
                    url_match = re.search(r'https?://[^\s]+', line_strip)
                    if url_match:
                        current_exercise["video"] = url_match.group()

        elif current_section == "modalities":
            if line_strip.startswith("- ") or line_strip.startswith("* "):
                sections["modalities"].append(line_strip[2:])
            elif ":" in line_strip and len(line_strip) < 150:
                sections["modalities"].append(line_strip)

        elif current_section == "instructions":
            if line_strip.startswith("- ") or line_strip.startswith("* "):
                sections["instructions"].append(line_strip[2:])

        elif current_section == "precautions":
            if line_strip.startswith("- ") or line_strip.startswith("* "):
                sections["precautions"].append(line_strip[2:])

    return sections
