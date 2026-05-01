"""
PhysioAssist PDF Generator v3
- Full detailed report (PDF 1)
- Quick Reference Card (PDF 2)
- Arabic language support (arabic-reshaper + bidi)
- Clickable YouTube links
"""

import re
import os
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

FONT_DIR = "/tmp/physio_fonts"
ARABIC_FONT_PATH = os.path.join(FONT_DIR, "NotoSansArabic.ttf")
ARABIC_FONT_URL = "https://fonts.gstatic.com/s/notosansarabic/v18/nwpxtLGrOAZMl5nJ_wfgRg3DrWFZWsnVBJ_sS6tlqHHFlhQ5l3sQWIHPqzCfyGyvu3CBFQLaig.ttf"


def _ensure_arabic_font() -> bool:
    """Download Arabic font if not present. Returns True if available."""
    if os.path.exists(ARABIC_FONT_PATH):
        return True
    try:
        import urllib.request
        os.makedirs(FONT_DIR, exist_ok=True)
        urllib.request.urlretrieve(ARABIC_FONT_URL, ARABIC_FONT_PATH)
        return True
    except Exception as e:
        logger.warning(f"Arabic font download failed: {e}")
        return False


def _fix_arabic(text: str) -> str:
    """Reshape and apply bidi to Arabic text for proper PDF rendering."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


def _is_arabic(text: str) -> bool:
    """Check if text contains Arabic characters."""
    return bool(re.search(r'[\u0600-\u06FF]', text))


def _process_text(text: str, is_ar: bool) -> str:
    """Process text — apply Arabic reshaping if needed."""
    if is_ar and _is_arabic(text):
        return _fix_arabic(text)
    return text


def _safe_html(text: str) -> str:
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def _add_links(text: str) -> str:
    url_re = r'(https?://[^\s\)\]<>]+)'
    def replace(m):
        url = m.group(1)
        display = url if len(url) <= 55 else url[:52] + "..."
        return f'<link href="{url}"><u>{_safe_html(display)}</u></link>'
    return re.sub(url_re, replace, _safe_html(text))


def _register_arabic_font():
    """Register Arabic font with ReportLab if available."""
    try:
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        if _ensure_arabic_font():
            pdfmetrics.registerFont(TTFont('Arabic', ARABIC_FONT_PATH))
            return True
    except Exception as e:
        logger.warning(f"Arabic font registration failed: {e}")
    return False


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


def _make_styles(lang: str = "en", arabic_available: bool = False):
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

    BLUE   = HexColor("#1565C0")
    GREEN  = HexColor("#2E7D32")
    RED    = HexColor("#C62828")
    DARK   = HexColor("#212121")
    GRAY   = HexColor("#616161")

    is_ar = (lang == "ar")
    align = TA_RIGHT if is_ar else TA_LEFT
    body_font = "Arabic" if (is_ar and arabic_available) else "Helvetica"
    bold_font = "Arabic" if (is_ar and arabic_available) else "Helvetica-Bold"

    return {
        "title": ParagraphStyle("title", fontName=bold_font,
            fontSize=22, textColor=BLUE, leading=28, spaceAfter=2, alignment=TA_CENTER),
        "subtitle": ParagraphStyle("subtitle", fontName=body_font,
            fontSize=11, textColor=GRAY, leading=16, spaceAfter=14, alignment=TA_CENTER),
        "section": ParagraphStyle("section", fontName=bold_font,
            fontSize=13, textColor=BLUE, leading=18, spaceBefore=14, spaceAfter=6, alignment=align),
        "exercise_title": ParagraphStyle("ex_title", fontName=bold_font,
            fontSize=12, textColor=GREEN, leading=16, spaceBefore=12, spaceAfter=4, alignment=align),
        "body": ParagraphStyle("body", fontName=body_font,
            fontSize=10.5, textColor=DARK, leading=16, spaceBefore=2, spaceAfter=2, alignment=align),
        "bold_body": ParagraphStyle("bold_body", fontName=bold_font,
            fontSize=10.5, textColor=DARK, leading=16, spaceBefore=3, spaceAfter=2, alignment=align),
        "bullet": ParagraphStyle("bullet", fontName=body_font,
            fontSize=10.5, textColor=DARK, leading=15,
            leftIndent=14, spaceBefore=1, spaceAfter=1, alignment=align),
        "warning": ParagraphStyle("warning", fontName=bold_font,
            fontSize=10, textColor=RED, leading=14, spaceBefore=4, spaceAfter=4, alignment=align),
        "link": ParagraphStyle("link", fontName=body_font,
            fontSize=10, textColor=BLUE, leading=14, spaceBefore=2, spaceAfter=2, alignment=TA_LEFT),
        "disclaimer": ParagraphStyle("disclaimer", fontName=body_font,
            fontSize=9, textColor=GRAY, leading=13, spaceBefore=6, alignment=TA_CENTER),
        # Quick card
        "card_title": ParagraphStyle("card_title", fontName=bold_font,
            fontSize=18, textColor=BLUE, leading=24, spaceAfter=4, alignment=TA_CENTER),
        "card_section": ParagraphStyle("card_section", fontName=bold_font,
            fontSize=11, textColor=GREEN, leading=15, spaceBefore=10, spaceAfter=4, alignment=align),
        "card_body": ParagraphStyle("card_body", fontName=body_font,
            fontSize=10, textColor=DARK, leading=14, spaceBefore=1, spaceAfter=1, alignment=align),
        "card_bullet": ParagraphStyle("card_bullet", fontName=body_font,
            fontSize=10, textColor=DARK, leading=14,
            leftIndent=12, spaceBefore=1, spaceAfter=1, alignment=align),
    }


def _parse_report(report_text: str, styles: dict, lang: str = "en",
                  full: bool = True, arabic_available: bool = False):
    from reportlab.platypus import Paragraph, Spacer, HRFlowable
    from reportlab.lib.colors import HexColor

    DIVIDER = HexColor("#BDBDBD")
    is_ar = (lang == "ar")
    story = []

    def proc(t):
        return _process_text(t, is_ar) if arabic_available else t

    for line in report_text.split("\n"):
        line = line.rstrip()
        if not line:
            story.append(Spacer(1, 3))
            continue

        # Section header ===
        if line.startswith("===") and line.endswith("==="):
            txt = proc(line.strip("=").strip())
            story.append(HRFlowable(width="100%", thickness=0.5,
                color=DIVIDER, spaceBefore=8, spaceAfter=4))
            story.append(Paragraph(_safe_html(txt),
                styles["section"] if full else styles["card_section"]))
            continue

        # Section ### headers
        if line.startswith("###"):
            txt = proc(line.replace("#", "").strip())
            story.append(Paragraph(_safe_html(txt),
                styles["section"] if full else styles["card_section"]))
            continue

        # Exercise title
        if re.match(r'^EXERCISE\s+\d+:', line, re.IGNORECASE):
            story.append(Paragraph(_safe_html(proc(line)),
                styles["exercise_title"]))
            continue

        # Warning
        if line.upper().startswith("WARNING:") or "RED FLAG" in line.upper():
            story.append(Paragraph(f"\u26a0 {_add_links(proc(line))}",
                styles["warning"]))
            continue

        # YouTube/video link
        if "youtube.com" in line.lower() or "youtu.be" in line.lower():
            story.append(Paragraph(_add_links(line), styles["link"]))
            continue

        # Other URL
        if "profphysio.com" in line.lower() or "amazon.com" in line.lower():
            story.append(Paragraph(_add_links(line), styles["link"]))
            continue

        # Bullet
        if line.startswith("- ") or line.startswith("* "):
            content = _add_links(proc(line[2:]))
            story.append(Paragraph(f"\u2022 {content}",
                styles["bullet"] if full else styles["card_bullet"]))
            continue

        # Numbered
        if re.match(r'^\s*\d+\.', line):
            story.append(Paragraph(_add_links(proc(line)),
                styles["bullet"] if full else styles["card_bullet"]))
            continue

        # Step lines
        if re.match(r'^\s*Step\s+\d+:', line, re.IGNORECASE):
            story.append(Paragraph(_add_links(proc(line)),
                styles["bullet"] if full else styles["card_bullet"]))
            continue

        # Key: value
        if ":" in line and len(line) < 150 and not line.startswith("http"):
            parts = line.split(":", 1)
            key = _safe_html(proc(parts[0].strip()))
            val = _add_links(proc(parts[1].strip())) if len(parts) > 1 else ""
            if val:
                story.append(Paragraph(
                    f"<b>{key}:</b> {val}",
                    styles["body"] if full else styles["card_body"]))
            else:
                story.append(Paragraph(
                    f"<b>{_add_links(proc(line))}</b>",
                    styles["bold_body"] if full else styles["card_body"]))
            continue

        # Default
        story.append(Paragraph(_add_links(proc(line)),
            styles["body"] if full else styles["card_body"]))

    return story


def generate_full_pdf(report_text: str, patient_name: str, lang: str = "en") -> bytes:
    try:
        from reportlab.platypus import Paragraph, Spacer, HRFlowable
        from reportlab.lib.colors import HexColor
        from reportlab.lib.units import cm

        arabic_ok = _register_arabic_font() if lang == "ar" else False

        buf = BytesIO()
        doc = _make_doc(buf, f"PhysioAssist Report - {patient_name}")
        styles = _make_styles(lang, arabic_ok)

        is_ar = (lang == "ar")

        def proc(t):
            return _process_text(t, is_ar) if arabic_ok else t

        story = []

        # Header
        story.append(Paragraph("PhysioAssist", styles["title"]))
        pat_label = proc(f"\u062a\u0642\u0631\u064a\u0631 \u0627\u0644\u062a\u0642\u064a\u064a\u0645 | {patient_name}") \
            if is_ar else f"Physical Therapy Assessment Report | {_safe_html(patient_name)}"
        story.append(Paragraph(pat_label, styles["subtitle"]))
        story.append(HRFlowable(width="100%", thickness=2,
            color=HexColor("#1565C0"), spaceAfter=16))

        # Report body
        story.extend(_parse_report(report_text, styles, lang, full=True,
                                   arabic_available=arabic_ok))

        # Disclaimer
        story.append(Spacer(1, 0.4*cm))
        story.append(HRFlowable(width="100%", thickness=0.5,
            color=HexColor("#BDBDBD"), spaceAfter=8))
        disc = (
            "\u0644\u0623\u063a\u0631\u0627\u0636 \u062a\u0639\u0644\u064a\u0645\u064a\u0629 "
            "\u0641\u0642\u0637. \u0644\u064a\u0633 \u0628\u062f\u064a\u0644\u0627\u064b "
            "\u0639\u0646 \u0627\u0644\u062a\u0634\u062e\u064a\u0635 \u0627\u0644\u0645\u0647\u0646\u064a. "
            "| PhysioAssist"
        ) if is_ar else (
            "Educational purposes only. Not a substitute for professional diagnosis. "
            "Consult a licensed physiotherapist. | PhysioAssist"
        )
        story.append(Paragraph(proc(disc) if arabic_ok else disc, styles["disclaimer"]))

        doc.build(story)
        return buf.getvalue()

    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return f"PDF Error: {e}\n\n{report_text}".encode("utf-8")


def generate_quick_card_pdf(report_text: str, patient_name: str, lang: str = "en") -> bytes:
    try:
        from reportlab.platypus import Paragraph, Spacer, HRFlowable
        from reportlab.lib.colors import HexColor
        from reportlab.lib.units import cm

        arabic_ok = _register_arabic_font() if lang == "ar" else False

        buf = BytesIO()
        doc = _make_doc(buf, f"PhysioAssist Quick Card - {patient_name}")
        styles = _make_styles(lang, arabic_ok)

        is_ar = (lang == "ar")

        def proc(t):
            return _process_text(t, is_ar) if arabic_ok else t

        sections = _extract_quick_sections(report_text)
        story = []

        # Header
        title_txt = proc("PhysioAssist \u2014 \u0628\u0637\u0627\u0642\u0629 \u0645\u0631\u062c\u0639\u064a\u0629") \
            if is_ar else "PhysioAssist \u2014 Quick Reference Card"
        story.append(Paragraph(title_txt, styles["card_title"]))

        pat_txt = proc(f"\u0627\u0644\u0645\u0631\u064a\u0636: {patient_name}") \
            if is_ar else f"Patient: {_safe_html(patient_name)}"
        story.append(Paragraph(pat_txt, styles["subtitle"]))
        story.append(HRFlowable(width="100%", thickness=2,
            color=HexColor("#1565C0"), spaceAfter=12))

        # Diagnosis
        if sections.get("diagnosis"):
            label = proc("\U0001f3af \u0627\u0644\u062a\u0634\u062e\u064a\u0635") if is_ar \
                else "\U0001f3af Diagnosis"
            story.append(Paragraph(label, styles["card_section"]))
            story.append(Paragraph(
                _safe_html(proc(sections["diagnosis"]) if arabic_ok else sections["diagnosis"]),
                styles["card_body"]
            ))
            story.append(HRFlowable(width="100%", thickness=0.3,
                color=HexColor("#E0E0E0"), spaceAfter=4))

        # Exercises
        if sections.get("exercises"):
            label = proc("\U0001f3cb \u062a\u0645\u0627\u0631\u064a\u0646\u0643") if is_ar \
                else "\U0001f3cb Your Exercises"
            story.append(Paragraph(label, styles["card_section"]))
            for ex in sections["exercises"][:4]:
                name = proc(ex["name"]) if arabic_ok else ex["name"]
                dose = proc(ex["dose"]) if arabic_ok else ex["dose"]
                story.append(Paragraph(
                    f"\u2022 <b>{_safe_html(name)}</b>: {_safe_html(dose)}",
                    styles["card_bullet"]
                ))
                if ex.get("video"):
                    story.append(Paragraph(
                        f"  \U0001f3ac {_add_links(ex['video'])}",
                        styles["link"]
                    ))
            story.append(HRFlowable(width="100%", thickness=0.3,
                color=HexColor("#E0E0E0"), spaceAfter=4))

        # Modalities
        if sections.get("modalities"):
            label = proc("\u2744\ufe0f\U0001f525 \u0639\u0644\u0627\u062c \u0645\u0646\u0632\u0644\u064a") \
                if is_ar else "\u2744\ufe0f\U0001f525 Home Physical Therapy"
            story.append(Paragraph(label, styles["card_section"]))
            for item in sections["modalities"][:5]:
                txt = proc(item) if arabic_ok else item
                story.append(Paragraph(f"\u2022 {_safe_html(txt)}", styles["card_bullet"]))
            story.append(HRFlowable(width="100%", thickness=0.3,
                color=HexColor("#E0E0E0"), spaceAfter=4))

        # Instructions
        if sections.get("instructions"):
            label = proc("\u2705 \u062a\u0639\u0644\u064a\u0645\u0627\u062a \u0623\u0633\u0627\u0633\u064a\u0629") \
                if is_ar else "\u2705 Key Instructions"
            story.append(Paragraph(label, styles["card_section"]))
            for item in sections["instructions"][:5]:
                txt = proc(item) if arabic_ok else item
                story.append(Paragraph(f"\u2022 {_safe_html(txt)}", styles["card_bullet"]))
            story.append(HRFlowable(width="100%", thickness=0.3,
                color=HexColor("#E0E0E0"), spaceAfter=4))

        # Precautions
        if sections.get("precautions"):
            label = proc("\U0001f6ab \u0645\u0648\u0627\u0646\u0639") if is_ar \
                else "\U0001f6ab Do NOT Do"
            story.append(Paragraph(label, styles["card_section"]))
            for item in sections["precautions"][:4]:
                txt = proc(item) if arabic_ok else item
                story.append(Paragraph(f"\u274c {_safe_html(txt)}", styles["card_bullet"]))

        # Follow-up
        if sections.get("followup"):
            label = proc("\U0001f4c5 \u062e\u0637\u0629 \u0627\u0644\u0645\u062a\u0627\u0628\u0639\u0629") \
                if is_ar else "\U0001f4c5 Follow-up Plan"
            story.append(Paragraph(label, styles["card_section"]))
            for item in sections["followup"][:3]:
                txt = proc(item) if arabic_ok else item
                story.append(Paragraph(f"\u2022 {_safe_html(txt)}", styles["card_bullet"]))

        # Footer
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width="100%", thickness=0.5,
            color=HexColor("#BDBDBD"), spaceAfter=6))
        disc = proc(
            "PhysioAssist | \u0644\u0623\u063a\u0631\u0627\u0636 \u062a\u0639\u0644\u064a\u0645\u064a\u0629 \u0641\u0642\u0637"
        ) if (is_ar and arabic_ok) else \
            "PhysioAssist | For educational purposes only. Consult a licensed physiotherapist."
        story.append(Paragraph(disc, styles["disclaimer"]))

        doc.build(story)
        return buf.getvalue()

    except Exception as e:
        logger.error(f"Quick card error: {e}")
        return f"Quick Card Error: {e}".encode("utf-8")


def _extract_quick_sections(report_text: str) -> dict:
    sections = {
        "diagnosis":    "",
        "exercises":    [],
        "modalities":   [],
        "instructions": [],
        "precautions":  [],
        "followup":     [],
    }

    lines = report_text.split("\n")
    current_section = None
    current_exercise = None

    for line in lines:
        ls = line.strip()

        upper = ls.upper()
        if "DIAGNOSIS" in upper or "CLINICAL" in upper:
            current_section = "diagnosis"
            continue
        elif "EXERCISE PROGRAM" in upper or "HOME EXERCISE" in upper or "PHASE 4" in upper:
            current_section = "exercises"
            continue
        elif any(w in upper for w in ["MODALI", "PHYSICAL THERAPY MODALI", "PHASE 6", "CRYOTHERAPY", "THERMOTHERAPY", "TENS"]):
            current_section = "modalities"
            continue
        elif any(w in upper for w in ["ACTIVITY MODIF", "OCCUPATION", "PHASE 7", "DAILY"]):
            current_section = "instructions"
            continue
        elif any(w in upper for w in ["CONTRAIND", "PRECAUTION", "PHASE 8", "AVOID"]):
            current_section = "precautions"
            continue
        elif any(w in upper for w in ["FOLLOW-UP", "PHASE 11", "FOLLOW UP"]):
            current_section = "followup"
            continue
        elif ls.startswith("===") or ls.startswith("###"):
            current_section = None
            current_exercise = None
            continue

        if not ls:
            continue

        if current_section == "diagnosis" and not sections["diagnosis"]:
            if any(w in ls.lower() for w in ["primary diagnosis", "most likely", "icd-10", "diagnosis:"]):
                sections["diagnosis"] = ls.split(":", 1)[-1].strip()[:120]

        elif current_section == "exercises":
            ex_m = re.match(r'^EXERCISE\s+(\d+):\s*(.+)', ls, re.IGNORECASE)
            if ex_m:
                current_exercise = {"name": ex_m.group(2)[:60], "dose": "", "video": ""}
                sections["exercises"].append(current_exercise)
            elif current_exercise:
                if re.search(r'sets|reps|PRESCRIPTION', ls, re.IGNORECASE):
                    current_exercise["dose"] = ls.split(":", 1)[-1].strip()[:80]
                elif "youtube.com" in ls.lower() or "youtu.be" in ls.lower():
                    url_m = re.search(r'https?://[^\s]+', ls)
                    if url_m:
                        current_exercise["video"] = url_m.group()

        elif current_section == "modalities":
            if ls.startswith(("- ", "* ")):
                sections["modalities"].append(ls[2:][:100])
            elif ":" in ls and len(ls) < 120 and not ls.startswith("http"):
                sections["modalities"].append(ls[:100])

        elif current_section == "instructions":
            if ls.startswith(("- ", "* ")):
                sections["instructions"].append(ls[2:][:100])

        elif current_section == "precautions":
            if ls.startswith(("- ", "* ")):
                sections["precautions"].append(ls[2:][:100])

        elif current_section == "followup":
            if ls.startswith(("- ", "* ")) or "week" in ls.lower() or "month" in ls.lower():
                sections["followup"].append(ls.lstrip("- *")[:100])

    return sections
