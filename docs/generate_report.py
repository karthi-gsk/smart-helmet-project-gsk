#!/usr/bin/env python3
"""
generate_report.py
Generates a professionally formatted, college-submission-ready DOCX & PDF report for the
AI-Powered Smart Helmet with Accident Prediction and Emergency Alert System.

College formatting guidelines applied:
- Paper: A4 (21.0 x 29.7 cm)
- Margins: 1.5" Left, 1.0" Right, 1.0" Top, 1.0" Bottom
- Font: Times New Roman throughout
- Content: 12pt, 1.5 line spacing, 1.27cm first-line indent
- Chapter Headings: 14pt, Bold, ALL CAPS, Center-aligned
- Sub-headings: 12pt, Bold, Left-aligned
- Page Numbering:
  * Cover page: No visible page number
  * Preliminary pages: Roman numerals (ii, iii, iv, v, vi, vii, viii), Center-bottom
  * Main chapters & appendices: Arabic numerals (1, 2, 3...), starting at 1 for Chapter 1, Center-bottom
- Dot leaders for TOC, List of Figures, List of Tables
- Diagrams: Included as centered images in Chapter 6 (System Architecture, DFD, Use Case, Activity, Sequence, Class)
- Screenshots: Included as centered images in Chapter 9 (Fig. 7 to Fig. 17)
- Tables: Repeating header row on split (`tblHeader`), row split prevention (`cantSplit`), captions above tables
"""

import os
import sys
import json
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls


def add_page_border(section):
    xml_str = (
        f'<w:pgBorders {nsdecls("w")} w:offsetFrom="page">'
        f'<w:top w:val="single" w:sz="8" w:space="24" w:color="000000"/>'
        f'<w:left w:val="single" w:sz="8" w:space="24" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="24" w:color="000000"/>'
        f'<w:right w:val="single" w:sz="8" w:space="24" w:color="000000"/>'
        f'</w:pgBorders>'
    )
    section._sectPr.append(parse_xml(xml_str))
from docx.enum.section import WD_SECTION_START
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "report_assets")
OUTPUT_DOCX = os.path.join(SCRIPT_DIR, "PROJECT_REPORT.docx")
OUTPUT_PDF = os.path.join(SCRIPT_DIR, "PROJECT_REPORT.pdf")
PAGE_MAP_FILE = os.path.join(SCRIPT_DIR, "page_map.json")

# Broken hyphen / invisible control-character replacements
TEXT_REPLACEMENTS = {
    "web\u00adbased": "web-based",
    "web\ufffebased": "web-based",
    "two\u00adwheeler": "two-wheeler",
    "two\ufffewheeler": "two-wheeler",
    "real\u00adtime": "real-time",
    "real\ufffetime": "real-time",
    "At\u00adRisk": "At-Risk",
    "At\ufffeRisk": "At-Risk",
    "well\u00addocumented": "well-documented",
    "well\ufffedocumented": "well-documented",
    "/api/demo\u00admode": "/api/demo-mode",
    "/api/demo\ufffemode": "/api/demo-mode",
    "red\u00adgold": "red-gold",
    "red\ufffegold": "red-gold",
}


def sanitize_text(text):
    """Normalize broken soft hyphens and stray control characters in report text."""
    if not text:
        return text
    for bad, good in TEXT_REPLACEMENTS.items():
        text = text.replace(bad, good)
    text = text.replace("\u00ad", "-")
    text = text.replace("\ufffe", "")
    text = text.replace("\ufeff", "")
    text = text.replace("\u200b", "")
    return text


# ─── HELPER UTILITIES ────────────────────────────────────────────────

def set_cell_shading(cell, color_hex):
    """Apply background colour to a table cell."""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_margins(section):
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.5)
    section.right_margin = Inches(1.0)


def add_page_number_to_footer(section):
    """Add a centered page number field to the section footer."""
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.text = ""
    
    run1 = p.add_run()
    fld1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    run1._r.append(fld1)
    
    run2 = p.add_run()
    instr = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
    run2._r.append(instr)
    
    run3 = p.add_run()
    fld2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    run3._r.append(fld2)
    
    for r in [run1, run2, run3]:
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)


def set_section_page_numbering(section, fmt="decimal", start=None):
    """Configure section page numbering format (decimal vs lowerRoman) and starting number."""
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is None:
        pgNumType = OxmlElement('w:pgNumType')
        sectPr.append(pgNumType)
    if fmt is not None:
        pgNumType.set(qn('w:fmt'), fmt)
    if start is not None:
        pgNumType.set(qn('w:start'), str(start))


def add_chapter_heading(doc, text):
    """14pt, bold, centre, ALL CAPS."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text.upper())
    run.bold = True
    run.font.size = Pt(14)
    run.font.name = "Times New Roman"
    return p


def add_sub_heading(doc, text, level=2):
    """12pt, bold, left-aligned sub-heading."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(12)
    run.font.name = "Times New Roman"
    return p


def add_body(doc, text):
    """12pt body paragraph with first-line indent and 1.5 line spacing."""
    text = sanitize_text(text)
    p = doc.add_paragraph()
    fmt = p.paragraph_format
    fmt.first_line_indent = Cm(1.27)   # 0.5 inch tab
    fmt.space_after = Pt(6)
    fmt.line_spacing = 1.5
    run = p.add_run(text)
    run.font.size = Pt(12)
    run.font.name = "Times New Roman"
    return p


def add_body_no_indent(doc, text):
    text = sanitize_text(text)
    p = doc.add_paragraph()
    fmt = p.paragraph_format
    fmt.space_after = Pt(6)
    fmt.line_spacing = 1.5
    run = p.add_run(text)
    run.font.size = Pt(12)
    run.font.name = "Times New Roman"
    return p


def add_bullet(doc, text):
    text = sanitize_text(text)
    p = doc.add_paragraph()
    fmt = p.paragraph_format
    fmt.left_indent = Cm(1.27)
    fmt.first_line_indent = Cm(-0.63)
    fmt.space_after = Pt(4)
    fmt.line_spacing = 1.5
    
    run_bullet = p.add_run("• ")
    run_bullet.bold = True
    run_bullet.font.size = Pt(12)
    run_bullet.font.name = "Times New Roman"
    
    run_text = p.add_run(text)
    run_text.font.size = Pt(12)
    run_text.font.name = "Times New Roman"
    return p


def add_figure_caption(doc, caption_text):
    """Bold italic, centred, 12pt below figures."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(14)
    run = p.add_run(caption_text)
    run.bold = True
    run.italic = True
    run.font.size = Pt(12)
    run.font.name = "Times New Roman"
    return p


def add_table_caption(doc, caption_text):
    """Bold, left-aligned, 12pt placed ABOVE tables."""
    caption_text = sanitize_text(caption_text)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.keep_together = True
    run = p.add_run(caption_text)
    run.bold = True
    run.font.size = Pt(12)
    run.font.name = "Times New Roman"
    return p


def add_image_centered(doc, path, width_inches=5.7):
    """Insert image centred with border formatting."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    if os.path.exists(path):
        run = p.add_run()
        run.add_picture(path, width=Inches(width_inches))
    else:
        run = p.add_run(f"[Image Placeholder: {os.path.basename(path)}]")
        run.italic = True
        run.font.size = Pt(11)
        run.font.name = "Times New Roman"
    return p


def add_dot_leader_entry(doc, title_text, page_str, bold=False):
    """Add a TOC / List line with dot leaders right-aligned to page number."""
    p = doc.add_paragraph()
    fmt = p.paragraph_format
    fmt.space_after = Pt(3)
    fmt.line_spacing = 1.5
    fmt.tab_stops.add_tab_stop(Inches(5.75), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    
    run1 = p.add_run(title_text)
    run1.font.name = "Times New Roman"
    run1.font.size = Pt(12)
    if bold:
        run1.bold = True
        
    run2 = p.add_run(f"\t{page_str}")
    run2.font.name = "Times New Roman"
    run2.font.size = Pt(12)
    if bold:
        run2.bold = True
    return p


def make_table(doc, headers, rows, col_widths=None):
    """Create a professionally formatted table with header repeating and cantSplit."""
    headers = [sanitize_text(h) for h in headers]
    rows = [[sanitize_text(str(val)) for val in row] for row in rows]

    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"

    tblPr = table._tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        table._tbl.insert(0, tblPr)
    tblPr.append(parse_xml(f'<w:keepNext {nsdecls("w")}/>'))

    # Header row
    hdr_trPr = table.rows[0]._tr.get_or_add_trPr()
    hdr_trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    hdr_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(11)
        run.font.name = "Times New Roman"
        set_cell_shading(cell, "D9E2F3")

    # Data rows
    for r_idx, row in enumerate(rows):
        row_trPr = table.rows[r_idx + 1]._tr.get_or_add_trPr()
        row_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(str(val))
            run.font.size = Pt(10.5)
            run.font.name = "Times New Roman"

    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Inches(w)
    return table


def add_table_block(doc, caption_text, headers, rows, col_widths=None, page_break_before=False):
    """Insert caption and table together; optionally start on a fresh page."""
    if page_break_before:
        doc.add_page_break()
    add_table_caption(doc, caption_text)
    make_table(doc, headers, rows, col_widths=col_widths)


def add_code_block(doc, code_text):
    """Monospace code block box."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.left_indent = Cm(1)
    p.paragraph_format.keep_together = True  # Keep code blocks together
    run = p.add_run(code_text)
    run.font.name = "Courier New"
    run.font.size = Pt(8.5)
    return p


# ═══════════════════════════════════════════════════════════════════
#  BUILD REPORT DOCUMENT
# ═══════════════════════════════════════════════════════════════

def build_report(page_map=None):
    if page_map is None:
        page_map = {}

    doc = Document()

    # Default styles
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(12)
    fmt = style.paragraph_format
    fmt.line_spacing = 1.5
    fmt.space_after = Pt(6)

    # ──────────────────────────────
    #  SECTION 1: COVER / TITLE PAGE (No Page Number)
    # ──────────────────────────────
    # ──────────────────────────────
    #  SECTION 1: COVER / TITLE PAGE (No Page Number, Page Border ON)
    # ──────────────────────────────
    sec1 = doc.sections[0]
    set_margins(sec1)
    sec1.page_height = Cm(29.7)
    sec1.page_width = Cm(21.0)
    add_page_border(sec1)
    
    # Ensure cover footer is empty and unlinked
    footer1 = sec1.footer
    footer1.is_linked_to_previous = False
    for p in footer1.paragraphs:
        p.text = ""

    # University Heading First at Top
    p_u1 = doc.add_paragraph()
    p_u1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_u1.paragraph_format.space_before = Pt(24)
    p_u1.paragraph_format.space_after = Pt(2)
    run_u1 = p_u1.add_run("Dr. M.G.R.\nEducational and Research Institute\n(Deemed to be University)")
    run_u1.bold = True
    run_u1.font.size = Pt(15)
    run_u1.font.name = "Times New Roman"

    p_sub1 = doc.add_paragraph()
    p_sub1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub1.paragraph_format.space_after = Pt(28)
    run_sub1 = p_sub1.add_run("(Declared under Section 3 of UGC Act 1956)")
    run_sub1.italic = True
    run_sub1.font.size = Pt(10)
    run_sub1.font.name = "Times New Roman"

    # Project Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(28)
    p_title.paragraph_format.line_spacing = 1.25
    run_title = p_title.add_run("AI-POWERED SMART HELMET\nWITH ACCIDENT PREDICTION AND\nEMERGENCY ALERT SYSTEM")
    run_title.bold = True
    run_title.font.size = Pt(17)
    run_title.font.name = "Times New Roman"

    # Mini Project Report Designation
    p_rep = doc.add_paragraph()
    p_rep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rep.paragraph_format.space_after = Pt(4)
    run_rep = p_rep.add_run("A MINI PROJECT REPORT")
    run_rep.bold = True
    run_rep.font.size = Pt(13)
    run_rep.font.name = "Times New Roman"

    p_subm = doc.add_paragraph()
    p_subm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subm.paragraph_format.space_after = Pt(16)
    run_subm = p_subm.add_run("Submitted in partial fulfillment of the requirements\nfor the award of the degree of")
    run_subm.font.size = Pt(11)
    run_subm.font.name = "Times New Roman"

    # Degree Wording
    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_after = Pt(16)
    p_deg.paragraph_format.line_spacing = 1.25
    run_deg = p_deg.add_run("Bachelor of Technology\nin\nComputer Science and Engineering (Artificial Intelligence and Data Science)")
    run_deg.bold = True
    run_deg.font.size = Pt(12)
    run_deg.font.name = "Times New Roman"

    # Department Line
    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_after = Pt(24)
    run_dept = p_dept.add_run("Department of Computer Science and Engineering (AI & DS)")
    run_dept.bold = True
    run_dept.font.size = Pt(12)
    run_dept.font.name = "Times New Roman"

    # Submitted By Block
    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_after = Pt(4)
    run_by = p_by.add_run("Submitted by:")
    run_by.font.size = Pt(11)
    run_by.font.name = "Times New Roman"

    for name in ["KARTHICK S", "MIDHUN SATHISHKUMAR", "KAMESH KUMAR J"]:
        p_name = doc.add_paragraph()
        p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_name.paragraph_format.space_after = Pt(3)
        run_n = p_name.add_run(name)
        run_n.bold = True
        run_n.font.size = Pt(12)
        run_n.font.name = "Times New Roman"

    # Academic Year
    p_year = doc.add_paragraph()
    p_year.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_year.paragraph_format.space_before = Pt(28)
    run_yr = p_year.add_run("Academic Year: 2025 - 2026")
    run_yr.bold = True
    run_yr.font.size = Pt(12)
    run_yr.font.name = "Times New Roman"

    # ──────────────────────────────
    #  SECTION 2: CERTIFICATE PAGE (Page Border ON, Roman Numerals: ii)
    # ──────────────────────────────
    sec2 = doc.add_section(WD_SECTION_START.NEW_PAGE)
    set_margins(sec2)
    add_page_border(sec2)
    add_page_number_to_footer(sec2)
    set_section_page_numbering(sec2, fmt="lowerRoman", start=2)  # Certificate is ii

    # University Heading First on Certificate Page
    p_u2 = doc.add_paragraph()
    p_u2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_u2.paragraph_format.space_before = Pt(0)
    p_u2.paragraph_format.space_after = Pt(2)
    run_u2 = p_u2.add_run("Dr. M.G.R.\nEDUCATIONAL AND RESEARCH INSTITUTE\n(Deemed to be University)")
    run_u2.bold = True
    run_u2.font.size = Pt(14)
    run_u2.font.name = "Times New Roman"

    p_dept2 = doc.add_paragraph()
    p_dept2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept2.paragraph_format.space_after = Pt(14)
    run_d2 = p_dept2.add_run("Department of Computer Science and Engineering (AI & DS)")
    run_d2.bold = True
    run_d2.font.size = Pt(12)
    run_d2.font.name = "Times New Roman"

    # Bonafide Certificate Heading
    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_after = Pt(14)
    run_c = p_cert.add_run("BONAFIDE CERTIFICATE")
    run_c.bold = True
    run_c.font.size = Pt(15)
    run_c.font.name = "Times New Roman"

    # Body
    add_body(doc,
        'This is to certify that the Mini Project entitled "AI-POWERED SMART HELMET WITH '
        'ACCIDENT PREDICTION AND EMERGENCY ALERT SYSTEM" is a bonafide work carried out by '
        'Karthick S, Midhun Sathishkumar, and Kamesh Kumar J in partial fulfillment of the '
        'requirements for the award of the degree of Bachelor of Technology in Computer Science '
        'and Engineering (Artificial Intelligence and Data Science) from Dr. M.G.R. Educational and '
        'Research Institute during the academic year 2025 - 2026.')

    for _ in range(2):
        doc.add_paragraph()

    table = doc.add_table(rows=3, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    labels = [
        ("Internal Guide", "Head of Department"),
        ("Name: ___________________", "Name: ___________________"),
        ("Signature: _______________", "Signature: _______________"),
    ]
    for r, (l, r_text) in enumerate(labels):
        for c, txt in enumerate([l, r_text]):
            cell = table.rows[r].cells[c]
            cell.text = ""
            p = cell.paragraphs[0]
            run = p.add_run(txt)
            run.font.size = Pt(12)
            run.font.name = "Times New Roman"
            if r == 0:
                run.bold = True

    # ──────────────────────────────
    #  SECTION 3: OTHER PRELIMINARY PAGES (No Border, Roman Numerals: iii, iv, v, vi, vii)
    # ──────────────────────────────
    sec3 = doc.add_section(WD_SECTION_START.NEW_PAGE)
    set_margins(sec3)
    add_page_number_to_footer(sec3)
    set_section_page_numbering(sec3, fmt="lowerRoman", start=3)

    # Acknowledgement
    add_chapter_heading(doc, "Acknowledgement")
    add_body(doc,
        'We would like to express our sincere gratitude to our project guide and the faculty '
        'of the Department of Computer Science and Engineering (AI & DS) at Dr. M.G.R. Educational and '
        'Research Institute for their continuous support, encouragement, and valuable guidance '
        'throughout the course of this mini project.')
    add_body(doc,
        'We extend our heartfelt thanks to the Head of the Department for providing us with '
        'the necessary resources and infrastructure to carry out this project successfully.')
    add_body(doc,
        'We are also grateful to our friends and family for their moral support and motivation '
        'during the development of this project.')
    add_body(doc,
        'Finally, we thank all the open-source communities and documentation authors whose '
        'tools, libraries, and resources made this project possible.')
    doc.add_paragraph()
    for name in ["Karthick S", "Midhun Sathishkumar", "Kamesh Kumar J"]:
        p = doc.add_paragraph()
        run = p.add_run(name)
        run.bold = True
        run.font.size = Pt(12)

    # Abstract
    doc.add_page_break()
    add_chapter_heading(doc, "Abstract")
    add_body(doc,
        'Road accidents involving two-wheeler vehicles constitute a significant proportion of global '
        'traffic fatalities. Key contributing factors include overspeeding, riding under the influence '
        'of alcohol, rider drowsiness, and delayed emergency medical response during the critical '
        '"Golden Hour." Traditional helmets provide only passive physical protection and lack intelligent '
        'features for proactive safety monitoring. '
        'This project presents an AI-Powered Smart Helmet with Accident Prediction and Emergency Alert '
        'System, a full-stack software prototype that demonstrates the integration of Artificial '
        'Intelligence, Internet of Things (IoT), and Machine Learning technologies for motorcycle rider '
        'safety. The system employs a Random Forest Classifier trained on synthetic sensor data to predict '
        'rider conditions across three classes: Safe, At-Risk, and Danger.')
    add_body(doc,
        'The current prototype is a 50% Working Software Prototype that uses simulated sensor data to '
        'demonstrate the complete system pipeline. The backend is built using Python FastAPI, which '
        'processes sensor telemetry, executes real-time ML predictions, and manages emergency alert '
        'dispatching. The frontend is a modern React.js web dashboard built with Vite, providing live '
        'telemetry visualization, AI prediction panels, historical data charts, and an emergency SOS '
        'alert card with GPS location and Google Maps integration. '
        'The system supports five simulation modes (Safe, Risky, Drunk, Drowsy, and Crash), each '
        'demonstrating distinct rider conditions with corresponding sensor value patterns and AI '
        'predictions. In crash mode, the system automatically triggers an emergency SOS alert with GPS '
        'coordinates and simulated GSM SMS dispatch to emergency contacts.')
    add_body(doc,
        'Real hardware integration using ESP32 microcontrollers, MPU6050 accelerometers, MQ-3 alcohol '
        'sensors, NEO-6M GPS modules, and SIM800L GSM modules is planned as future scope to evolve this '
        'software prototype into a complete physical product.')

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    run = p.add_run('Keywords: ')
    run.bold = True
    run.font.size = Pt(12)
    run.font.name = "Times New Roman"
    run2 = p.add_run('Smart Helmet, Accident Prediction, Emergency Alert, Random Forest, IoT, '
                     'Machine Learning, Road Safety, GPS Tracking, GSM Alert')
    run2.italic = True
    run2.font.size = Pt(12)
    run2.font.name = "Times New Roman"

    # Table of Contents
    doc.add_page_break()
    add_chapter_heading(doc, "Table of Contents")

    toc_default_pages = {
        "Certificate": "ii",
        "Acknowledgement": "iii",
        "Abstract": "iv",
        "Table of Contents": "v",
        "List of Figures": "vi",
        "List of Tables": "vii",
        "Chapter 1: Introduction": "1",
        "Chapter 2: Problem Definition": "4",
        "Chapter 3: Objective of the Project": "6",
        "Chapter 4: Literature Survey": "7",
        "Chapter 5: Requirement Analysis": "9",
        "Chapter 6: System Design": "12",
        "Chapter 7: Implementation": "18",
        "Chapter 8: Modules Description": "21",
        "Chapter 9: Output and Screenshots": "23",
        "Chapter 10: Testing": "29",
        "Chapter 11: Advantages and Applications": "31",
        "Chapter 12: Limitations": "32",
        "Chapter 13: Future Scope": "33",
        "Chapter 14: Conclusion": "34",
        "Chapter 15: References / Bibliography": "35",
        "Appendix A: Backend API Details": "36",
        "Appendix B: Important Code Snippets": "37",
        "Appendix C: Run Commands": "39",
        "Appendix D: Demo Flow": "40",
        "Appendix E: Hardware Components List": "41",
    }

    for key, def_pg in toc_default_pages.items():
        pg = page_map.get(key, def_pg)
        bold = key.startswith("Chapter") or key in ["Certificate", "Acknowledgement", "Abstract", "Table of Contents", "List of Figures", "List of Tables"]
        add_dot_leader_entry(doc, key, str(pg), bold=bold)

    # List of Figures
    doc.add_page_break()
    add_chapter_heading(doc, "List of Figures")

    fig_default_pages = [
        ("Fig. 1: System Architecture Diagram", "12"),
        ("Fig. 2: Data Flow Diagram (Level-1)", "13"),
        ("Fig. 3: Use Case Diagram", "14"),
        ("Fig. 4: Activity Diagram", "15"),
        ("Fig. 5: Sequence Diagram", "16"),
        ("Fig. 6: Class Diagram", "17"),
        ("Fig. 7: Home Page of Smart Helmet Website", "23"),
        ("Fig. 8: Project Team Section", "24"),
        ("Fig. 9: Live Dashboard in Safe Mode", "24"),
        ("Fig. 10: Risky Mode Showing At-Risk Prediction", "25"),
        ("Fig. 11: Drunk Mode Showing Alcohol Detection", "25"),
        ("Fig. 12: Drowsy Mode Showing Fatigue Warning", "26"),
        ("Fig. 13: Crash Mode Showing Emergency SOS Alert", "26"),
        ("Fig. 14: GPS Location and Google Maps Link", "27"),
        ("Fig. 15: Project Modules Page", "27"),
        ("Fig. 16: Future Hardware Integration Diagram", "28"),
        ("Fig. 17: FastAPI Documentation Page", "28"),
    ]

    for title, def_pg in fig_default_pages:
        pg = page_map.get(title, def_pg)
        add_dot_leader_entry(doc, title, str(pg), bold=False)

    # List of Tables
    doc.add_page_break()
    add_chapter_heading(doc, "List of Tables")

    table_default_pages = [
        ("Table 1: Comparison of Existing and Proposed Systems", "9"),
        ("Table 2: Functional Requirements", "10"),
        ("Table 3: Non-Functional Requirements", "10"),
        ("Table 4: Software Requirements", "11"),
        ("Table 5: Hardware Requirements (Future Scope)", "11"),
        ("Table 6: ML Prediction Labels and Probabilities", "19"),
        ("Table 7: Simulation Mode Parameters", "20"),
        ("Table 8: Test Cases and Results", "29"),
    ]

    for title, def_pg in table_default_pages:
        pg = page_map.get(title, def_pg)
        add_dot_leader_entry(doc, title, str(pg), bold=False)

    # ──────────────────────────────
    #  SECTION 3: MAIN CHAPTERS & APPENDICES (Arabic Numerals starting at Page 1)
    # ──────────────────────────────
    sec3 = doc.add_section(WD_SECTION_START.NEW_PAGE)
    set_margins(sec3)
    add_page_number_to_footer(sec3)
    set_section_page_numbering(sec3, fmt="decimal", start=1)  # Chapter 1 is Page 1

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 1: INTRODUCTION
    # ═══════════════════════════════════════════════════════════════
    add_chapter_heading(doc, "Chapter 1: Introduction")

    add_sub_heading(doc, "1.1 Overview")
    add_body(doc,
        'The rapid expansion of two-wheeler usage in urban and rural areas has led to a corresponding '
        'increase in road accidents, particularly involving motorcycles. According to the World Health '
        'Organization (WHO), road traffic injuries are the leading cause of death among young people '
        'aged 15 to 29 years, and two-wheeler riders constitute a disproportionately large share of '
        'these casualties. Traditional helmets, while effective in providing physical protection to the '
        'skull, offer no intelligent capabilities for accident prediction, rider condition monitoring, '
        'or emergency communication.')
    add_body(doc,
        'This project, titled "AI-Powered Smart Helmet with Accident Prediction and Emergency Alert '
        'System," presents a technology-driven solution that transforms an ordinary helmet into an '
        'intelligent safety device. By integrating multiple sensors, a Machine Learning prediction '
        'engine, and an automated emergency alert mechanism, the system aims to significantly reduce '
        'accident-related fatalities by enabling proactive safety monitoring and rapid emergency response.')
    add_body(doc,
        'The current implementation is a 50% working software prototype that demonstrates the complete '
        'data pipeline - from sensor data acquisition (simulated) to AI-based risk prediction and '
        'emergency alert dispatch - via a live web-based dashboard. Real hardware '
        'integration is planned as future scope.')

    add_sub_heading(doc, "1.2 Road Safety and Two-Wheeler Accident Problem")
    add_body(doc,
        'Two-wheeler vehicles account for a significant percentage of overall traffic on Indian roads. '
        'The National Crime Records Bureau (NCRB) data indicates that India witnesses a disproportionately '
        'high number of road accident fatalities involving motorcycle riders compared to other vehicle categories. '
        'The primary causes include:')
    add_bullet(doc, "Overspeeding: Exceeding safe speed limits, especially on highways and poorly maintained roads, leads to loss of vehicle control.")
    add_bullet(doc, "Alcohol Impairment: Riding under the influence of alcohol severely compromises judgment, reaction time, and motor coordination.")
    add_bullet(doc, "Rider Fatigue and Drowsiness: Long-distance riders often experience microsleep episodes that lead to sudden loss of vehicular control.")
    add_bullet(doc, 'Delayed Emergency Response: In many accident scenarios, especially in remote areas or during nighttime, there is a significant delay between the accident occurrence and the arrival of medical help. This delay, often exceeding the critical "Golden Hour," substantially reduces survival rates.')

    add_sub_heading(doc, "1.3 Need for Smart Helmet System")
    add_body(doc,
        'The limitations of traditional helmets highlight the urgent need for a smart helmet system that can:')
    add_bullet(doc, "Continuously monitor rider parameters such as speed, body orientation, blood alcohol levels, and fatigue levels.")
    add_bullet(doc, "Predict potential dangers before they escalate into accidents by analyzing sensor patterns using Artificial Intelligence.")
    add_bullet(doc, "Automatically alert emergency services and family members with precise GPS location data in the event of a crash, without requiring manual intervention.")
    add_bullet(doc, "Prevent intoxicated riding by locking the vehicle ignition system when unsafe alcohol levels are detected.")

    add_sub_heading(doc, "1.4 Role of AI and IoT in Rider Safety")
    add_body(doc,
        'Artificial Intelligence (AI) enables the system to analyze multi-dimensional sensor data and '
        'classify rider conditions in real-time. Rather than relying on simple threshold-based rules, '
        'AI models such as Random Forest classifiers can learn complex non-linear relationships between '
        'sensor readings and safety outcomes, providing more accurate and reliable predictions.')
    add_body(doc,
        'Internet of Things (IoT) provides the framework for connecting physical sensors (accelerometers, '
        'alcohol sensors, GPS modules) to cloud-based processing systems via wireless communication '
        'protocols. IoT architecture enables real-time data streaming, remote monitoring, and automated '
        'response mechanisms.')
    add_body(doc,
        'The combination of AI and IoT in this project creates an intelligent safety ecosystem where '
        'sensors continuously collect rider and environmental data, AI algorithms process this data to '
        'predict risk levels, IoT communication channels transmit alerts to emergency services, and a '
        'web dashboard provides real-time visibility into rider safety status.')

    add_sub_heading(doc, "1.5 Purpose of the Project")
    add_body(doc,
        'The primary purpose of this project is to demonstrate the feasibility and effectiveness of an '
        'AI-powered smart helmet system through a working software prototype. The project aims to:')
    add_bullet(doc, "Showcase the integration of simulated IoT sensor data with a Machine Learning prediction model.")
    add_bullet(doc, "Provide a real-time web dashboard for monitoring rider safety status.")
    add_bullet(doc, "Simulate emergency alert mechanisms including GPS location tracking and SMS dispatch.")
    add_bullet(doc, "Serve as a foundation for future hardware implementation using actual sensors and microcontrollers.")
    add_bullet(doc, "Demonstrate practical applications of AI, IoT, and web technologies in the domain of road safety.")

    add_sub_heading(doc, "1.6 Scope of the Project")
    add_body(doc,
        'The scope of this project encompasses a full-stack web application comprising a FastAPI backend '
        '(Python) and a React.js frontend (Vite), a Random Forest Classifier trained on synthetic helmet '
        'sensor data, software-based simulation of sensor readings, a professional web dashboard, '
        'simulated crash detection with GPS and SOS, and five distinct simulation modes for demonstration.')
    add_body(doc,
        'Out of scope for the current version: Physical hardware prototype with real sensors, actual GSM '
        'SMS transmission, mobile application development, cloud database integration, and real-world '
        'accident dataset training.')

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 2: PROBLEM DEFINITION
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 2: Problem Definition")

    add_sub_heading(doc, "2.1 Existing Problem")
    add_body(doc,
        'Motorcycle accidents remain one of the most pressing road safety challenges worldwide. Despite '
        'advancements in vehicle technology and road network infrastructure, two-wheeler riders continue to face '
        'elevated risks due to their exposed riding position and the inherent instability of two-wheeled '
        'vehicles.')
    add_body(doc,
        'The existing approach to motorcycle safety relies primarily on passive helmets that only provide '
        'impact protection, manual accident reporting that depends on bystanders, and post-accident response '
        'where emergency services are activated only after an accident is reported. This reactive approach '
        'fails to address accident prevention and timely emergency response.')

    add_sub_heading(doc, "2.2 Limitations of Traditional Helmets")
    add_body(doc, 'Traditional motorcycle helmets suffer from several significant limitations:')
    add_bullet(doc, "No sensing capability: Traditional helmets cannot detect any parameters about the rider's condition.")
    add_bullet(doc, "No communication capability: No built-in mechanism to communicate with external systems or emergency services.")
    add_bullet(doc, "No predictive intelligence: Without sensors and processing, traditional helmets cannot anticipate dangers.")
    add_bullet(doc, "No accident detection: Cannot automatically detect that an accident has occurred.")
    add_bullet(doc, "No impairment detection: No capability to detect alcohol influence or dangerous fatigue.")

    add_sub_heading(doc, "2.3 Delayed Emergency Response Issue")
    add_body(doc,
        'One of the most critical factors in accident survival is the speed of emergency medical response. '
        'Medical research has established the concept of the "Golden Hour" - the critical time window '
        '(approximately 60 minutes) after a traumatic injury during which prompt medical treatment '
        'significantly improves survival rates.')
    add_body(doc,
        'In many motorcycle accident scenarios, especially those occurring in remote areas, during nighttime, '
        'single-vehicle accidents, or situations where the rider is unconscious, the delay between accident '
        'occurrence and emergency response arrival often exceeds the Golden Hour, dramatically reducing '
        'survival chances. An automated emergency alert system can significantly reduce this critical delay.')

    add_sub_heading(doc, "2.4 Alcohol, Drowsiness, and Risky Riding Problems")
    add_body(doc,
        'Riding under the influence of alcohol reduces reaction time, impairs judgment, compromises motor '
        'coordination, and induces overconfidence. Rider drowsiness leads to microsleep episodes, reduced '
        'situational awareness, and gradual loss of postural control. Overspeeding, aggressive acceleration, '
        'and sharp turns contribute to a large number of motorcycle accidents. Real-time monitoring of rider behavioral '
        'patterns helps identify at-risk conditions before accidents occur.')

    add_sub_heading(doc, "2.5 Problem Statement")
    add_body(doc,
        'Motorcycle riders face significant risks due to road accidents, unsafe riding behavior, delayed '
        'medical response, and lack of proactive safety systems. Traditional helmets provide physical '
        'protection but lack intelligent features that can predict accidents, monitor rider condition, or '
        'provide emergency communication.')
    add_body(doc,
        'There is a clear need for an intelligent helmet system that can continuously monitor rider '
        'parameters using multiple sensors, employ Artificial Intelligence to predict accident risk levels '
        'in real-time, automatically detect crash events and dispatch emergency alerts with GPS coordinates, '
        'detect and respond to alcohol impairment and rider drowsiness, and provide a real-time monitoring '
        'dashboard for safety oversight.')

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 3: OBJECTIVE OF THE PROJECT
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 3: Objective of the Project")

    add_body(doc, 'The primary objectives of this project are as follows:')
    add_bullet(doc, "To monitor rider safety using smart helmet sensor data: Design and implement a system that processes multiple sensor inputs - including speed, vibration, alcohol level, drowsiness score, 3-axis accelerometer, and 3-axis gyroscope data - to comprehensively assess the rider's condition.")
    add_bullet(doc, "To classify rider condition as Safe, At-Risk, or Danger: Develop a Machine Learning model (Random Forest Classifier) capable of analyzing the 10-dimensional sensor feature vector and classifying the rider's condition into three risk levels with associated confidence probabilities.")
    add_bullet(doc, "To detect risky riding, alcohol impairment, drowsiness, and crash conditions: Implement distinct detection mechanisms for overspeeding (Risky), elevated blood alcohol (Drunk), high fatigue index (Drowsy), and high-G impact (Crash).")
    add_bullet(doc, "To provide a real-time web dashboard: Build a professional, responsive web dashboard using React.js that displays live sensor telemetry, AI predictions, historical charts, and emergency alert information.")
    add_bullet(doc, "To simulate GPS-based emergency alert: Demonstrate an emergency SOS system that extracts GPS coordinates upon crash detection and generates a Google Maps link for emergency responders.")
    add_bullet(doc, "To demonstrate AI and IoT integration through a software prototype: Create a working 50% software prototype that demonstrates the complete pipeline from sensor data collection to AI prediction to emergency response.")
    add_bullet(doc, "To provide future scope for hardware implementation: Design the software architecture in a modular manner that allows straightforward integration with physical hardware components in future iterations.")

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 4: LITERATURE SURVEY
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 4: Literature Survey")

    add_sub_heading(doc, "4.1 Smart Helmet Systems")
    add_body(doc,
        'The concept of smart helmets has evolved significantly in recent years with the advancement of '
        'embedded systems and IoT technologies. Modern approaches integrate multiple sensors, wireless '
        'communication modules, and intelligent processing capabilities. Research has explored the use of '
        'MEMS sensors within helmet cavities for real-time data acquisition. The integration of '
        'microcontrollers such as Arduino and ESP32 has enabled on-device processing of sensor data.')

    add_sub_heading(doc, "4.2 IoT-Based Accident Detection Systems")
    add_body(doc,
        'IoT technology has been extensively applied in accident detection and emergency response systems. '
        'Approaches typically involve sensor nodes for data collection, wireless communication protocols '
        'for data transmission, and cloud-based processing for analysis and alert generation. Key challenges '
        'include power management, reliable communication, and minimizing false positives.')

    add_sub_heading(doc, "4.3 Alcohol Detection in Vehicle Safety")
    add_body(doc,
        'Breath alcohol detection using semiconductor-based gas sensors such as the MQ-3 has been widely '
        'researched. Studies have demonstrated integration with vehicle ignition systems to create alcohol '
        'interlock mechanisms. The concept of integrating alcohol detection within a helmet is particularly '
        'relevant for two-wheelers.')

    add_sub_heading(doc, "4.4 Drowsiness Detection Systems")
    add_body(doc,
        'Drowsiness detection approaches include vision-based methods using cameras, physiological '
        'signal-based methods monitoring EEG/EOG/EMG, and behavioral pattern-based methods analyzing '
        'driving patterns. For helmet-based systems, IR sensors for eye blink detection combined with '
        'accelerometer/gyroscope behavioral analysis provides a practical approach.')

    add_sub_heading(doc, "4.5 GPS and GSM Emergency Alert Systems")
    add_body(doc,
        'The combination of GPS receivers (NEO-6M) and GSM modules (SIM800L) has been extensively used in '
        'vehicle tracking and emergency alert systems. Including a direct Google Maps URL with GPS '
        'coordinates in SMS messages significantly improves emergency response efficiency.')

    add_sub_heading(doc, "4.6 Machine Learning for Risk Prediction")
    add_body(doc,
        'Machine Learning algorithms including Decision Trees, Random Forests, SVMs, and Neural Networks '
        'have been applied to road safety applications. For this project, the Random Forest Classifier was '
        'selected due to its high accuracy on tabular data, robustness against overfitting, fast inference '
        'time, and interpretability through feature importance analysis.')

    add_sub_heading(doc, "4.7 Summary of Literature Survey")
    add_body(doc,
        'The literature survey reveals that smart helmet technology is an active research area combining '
        'IoT, AI, and communication technologies. Multi-sensor fusion, ML classifiers, GPS-GSM integration, '
        'and software prototyping before hardware development are proven approaches.')

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 5: REQUIREMENT ANALYSIS
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 5: Requirement Analysis")

    add_sub_heading(doc, "5.1 Existing System")
    add_body(doc,
        'The existing system for motorcycle rider safety consists of conventional helmets that provide '
        'only passive physical protection. Helmets have no embedded sensors, accident detection relies on '
        'manual reporting, there is no real-time monitoring, and emergency response is delayed.')

    add_table_caption(doc, "Table 1: Comparison of Existing and Proposed Systems")
    make_table(doc,
        ["Feature", "Existing System", "Proposed System"],
        [
            ["Helmet Type", "Passive (physical protection only)", "Active (sensor-integrated)"],
            ["Accident Detection", "Manual (bystander reporting)", "Automatic (sensor-based)"],
            ["Risk Prediction", "Not available", "AI-based (Random Forest)"],
            ["Alcohol Detection", "Not available", "MQ-3 sensor-based"],
            ["Drowsiness Detection", "Not available", "IR sensor / fatigue score"],
            ["Emergency Alert", "Manual phone call", "Automated GPS + GSM SMS"],
            ["Real-time Monitoring", "Not available", "Web-based live dashboard"],
            ["Response Time", "15-60+ minutes", "Immediate automated alert"],
        ])

    add_sub_heading(doc, "5.2 Proposed System")
    add_body(doc,
        'The proposed system is an AI-Powered Smart Helmet that integrates multiple sensors, a Machine '
        'Learning prediction engine, and an automated emergency alert mechanism. The current implementation '
        'is a 50% working software prototype that simulates the complete system pipeline using FastAPI '
        'backend, Random Forest ML model, and React web dashboard.')

    doc.add_page_break()
    add_sub_heading(doc, "5.3 Functional Requirements")
    add_table_caption(doc, "Table 2: Functional Requirements")
    make_table(doc,
        ["ID", "Requirement", "Description"],
        [
            ["FR-01", "Display live sensor values", "Real-time values for speed, alcohol, drowsiness, vibration, accelerometer, gyroscope"],
            ["FR-02", "Switch simulation modes", "Switch between Safe, Risky, Drunk, Drowsy, Crash modes"],
            ["FR-03", "Predict rider state", "Predicts rider condition: Safe, At-Risk, Danger"],
            ["FR-04", "Detect alcohol condition", "Detect elevated alcohol and display warnings"],
            ["FR-05", "Detect drowsiness", "Detect high drowsiness scores and display fatigue warnings"],
            ["FR-06", "Detect crash condition", "Detect high-G impact and vibration spikes"],
            ["FR-07", "Display GPS location", "Show GPS coordinates with Google Maps link"],
            ["FR-08", "Show emergency SOS", "Display SOS card with crash details and GSM status"],
        ])

    doc.add_page_break()
    add_sub_heading(doc, "5.4 Non-Functional Requirements")
    add_table_caption(doc, "Table 3: Non-Functional Requirements")
    make_table(doc,
        ["ID", "Requirement", "Description"],
        [
            ["NFR-01", "User-friendly interface", "Intuitive, visually appealing dashboard"],
            ["NFR-02", "Fast response time", "Updates within 1 second"],
            ["NFR-03", "Demo mode accuracy", "Predictions consistent with selected mode"],
            ["NFR-04", "Scalability", "Supports future hardware integration"],
            ["NFR-05", "Maintainability", "Well-documented, modular codebase"],
            ["NFR-06", "Presentation readiness", "Suitable for live demonstration"],
        ])

    add_sub_heading(doc, "5.5 Software Requirements")
    add_table_caption(doc, "Table 4: Software Requirements")
    make_table(doc,
        ["Component", "Technology", "Details"],
        [
            ["Programming Language", "Python", "3.9+"],
            ["Backend Framework", "FastAPI", "Latest stable"],
            ["Frontend Framework", "React.js", "18.x with Vite 5.x"],
            ["ML Library", "Scikit-learn", "Random Forest Classifier"],
            ["Numerical Computing", "NumPy, Pandas", "Latest stable"],
            ["Chart Library", "Recharts", "React charting"],
            ["Icon Library", "Lucide-React", "SVG icons"],
            ["IDE", "VS Code / Antigravity IDE", "Development environment"],
        ])

    doc.add_page_break()
    add_sub_heading(doc, "5.6 Hardware Requirements (Future Scope)")
    add_table_caption(doc, "Table 5: Hardware Requirements (Future Scope)")
    make_table(doc,
        ["Component", "Specification", "Purpose"],
        [
            ["ESP32", "Dual-core, Wi-Fi + BLE", "Central microcontroller"],
            ["MPU6050", "6-axis accel + gyro", "Impact and orientation detection"],
            ["MQ-3 Sensor", "Semiconductor gas sensor", "Breath alcohol detection"],
            ["SW-420 Sensor", "Vibration sensor", "Mechanical impact detection"],
            ["NEO-6M GPS", "Satellite positioning", "Real-time location tracking"],
            ["SIM800L GSM", "Quad-band GSM", "Emergency SMS dispatch"],
            ["Active Buzzer", "Piezoelectric", "Audible warning alerts"],
            ["Relay Module", "5V relay", "Ignition lock control"],
            ["Helmet", "ISI-certified", "Physical housing"],
        ])
    add_body(doc,
        'Note: These hardware components are listed for future implementation. The current software '
        'prototype uses simulated sensor data.')

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 6: SYSTEM DESIGN
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 6: System Design")

    add_sub_heading(doc, "6.1 System Architecture")
    add_body(doc,
        'The system architecture follows a layered design pattern that separates concerns across '
        'hardware, communication, processing, and presentation layers. Layer 1 is the Sensor Hardware '
        'Layer (future scope) housing MPU6050, MQ-3, SW-420, NEO-6M, and IR sensors. Layer 2 is the '
        'ESP32 Microcontroller Layer. Layer 3 is the FastAPI Backend Processing Layer (implemented). '
        'Layer 4 is the AI/ML Prediction Layer with the Random Forest Classifier (implemented). '
        'Layer 5 is the React Frontend Presentation Layer (implemented). Layer 6 is the Emergency '
        'Alert Layer (simulated).')

    arch_path = os.path.join(ASSETS_DIR, "system_architecture.png")
    add_image_centered(doc, arch_path, width_inches=5.6)
    add_figure_caption(doc, "Fig. 1: System Architecture Diagram")

    add_sub_heading(doc, "6.2 Data Flow Diagram")
    add_body(doc,
        'The Level-1 Data Flow Diagram illustrates how data moves through the system. External entities '
        'include the Rider (generates sensor data), Emergency Contacts (receive SOS alerts), and Google '
        'Maps (location visualization). Key processes include Collect Sensor Data, Process and Predict '
        'Risk, Display Dashboard, and Trigger Emergency Alert. Data stores include the Sensor History '
        'Log and ML Model Store.')

    dfd_path = os.path.join(ASSETS_DIR, "data_flow_diagram.png")
    add_image_centered(doc, dfd_path, width_inches=5.6)
    add_figure_caption(doc, "Fig. 2: Data Flow Diagram (Level-1)")

    add_sub_heading(doc, "6.3 Use Case Diagram")
    add_body(doc,
        'The Use Case Diagram identifies primary actors (Rider, Emergency Contact, System Administrator) '
        'and their interactions with the system including View Live Dashboard, Select Simulation Mode, '
        'View Sensor Telemetry, View AI Risk Prediction, View GPS Location, Receive Emergency SOS Alert, '
        'View Historical Charts, Reset Alert, Train ML Model, and Configure Emergency Contacts.')

    uc_path = os.path.join(ASSETS_DIR, "use_case_diagram.png")
    add_image_centered(doc, uc_path, width_inches=5.6)
    add_figure_caption(doc, "Fig. 3: Use Case Diagram")

    add_sub_heading(doc, "6.4 Activity Diagram")
    add_body(doc,
        'The activity diagram depicts the complete system workflow: from system initialization and sensor '
        'data collection to AI risk prediction, branching on risk state, emergency alert execution upon crash '
        'detection, GPS coordinate extraction, SOS SMS dispatch simulation, and real-time dashboard updates.')

    act_path = os.path.join(ASSETS_DIR, "activity_diagram.png")
    add_image_centered(doc, act_path, width_inches=5.6)
    add_figure_caption(doc, "Fig. 4: Activity Diagram")

    add_sub_heading(doc, "6.5 Sequence Diagram")
    add_body(doc,
        'The sequence diagram shows the chronological interaction between the User, React Dashboard, '
        'FastAPI Backend, Random Forest Model, Sensor Simulation, and Emergency Alert System during '
        'mode selection, live data polling, and emergency SOS dispatch.')

    seq_path = os.path.join(ASSETS_DIR, "sequence_diagram.png")
    add_image_centered(doc, seq_path, width_inches=5.6)
    add_figure_caption(doc, "Fig. 5: Sequence Diagram")

    add_sub_heading(doc, "6.6 Class Diagram")
    add_body(doc,
        'The UML Class Diagram illustrates the object-oriented structure of the backend and frontend '
        'modules, detailing class attributes, methods, and relationships between HelmetState, DemoModeRequest, '
        'FastAPI App, RandomForestClassifier, and ReactDashboard.')

    cls_path = os.path.join(ASSETS_DIR, "class_diagram.png")
    add_image_centered(doc, cls_path, width_inches=5.6)
    add_figure_caption(doc, "Fig. 6: Class Diagram")

    add_sub_heading(doc, "6.7 Architecture Overview")
    add_body(doc,
        'The complete architecture diagram (Fig. 1) illustrates the end-to-end system showing data flow '
        'from the sensor hardware layer through communication and processing layers to the presentation '
        'and alert layers. The modular design ensures the simulation layer can be replaced with real '
        'hardware interfaces in future iterations without modifying core prediction and presentation logic.')

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 7: IMPLEMENTATION
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 7: Implementation")

    add_sub_heading(doc, "7.1 Implementation Overview")
    add_body(doc,
        'The implementation follows a modular full-stack architecture with clear separation between the '
        'backend processing layer and the frontend presentation layer. The backend directory contains the '
        'FastAPI server (main.py), ML model module (model.py), trained model file (helmet_model.joblib), '
        'and dependency specifications. The frontend directory contains the React application with Vite, '
        'page components, API layer, and styling.')

    add_sub_heading(doc, "7.2 Backend Implementation")
    add_body(doc,
        'The backend is built using Python FastAPI. It provides four REST API endpoints: GET /api/live-data '
        'returns current sensor telemetry, ML predictions, and historical readings. GET /api/alert returns '
        'the emergency alert status. POST demo mode endpoint switches the simulation to a specified mode. '
        'POST /api/reset-alert resets the alert state and returns to safe mode.')
    add_body(doc,
        'State management uses a singleton HelmetState object with a threading.Lock for thread-safe access. '
        'A daemon background thread runs continuously, calling simulate_state() every second to update '
        'sensor values based on the active demo mode. CORS middleware is configured for frontend access.')

    add_sub_heading(doc, "7.3 Frontend Implementation")
    add_body(doc,
        'The frontend is a React.js single-page application built with Vite. The Home page displays the '
        'project overview, problem definition, team section with role-based icons and contribution badges, '
        'and a future hardware integration diagram. The Live Dashboard features mode selector buttons, '
        'an AI prediction panel, six sensor telemetry cards, two historical trend charts (Recharts), '
        'and an emergency SOS card. The Modules page describes all eight project modules.')

    add_sub_heading(doc, "7.4 Machine Learning Implementation")
    add_body(doc,
        'The system uses a Random Forest Classifier from scikit-learn. The model is trained on 1,500 '
        'synthetically generated samples with 10 features (speed, vibration, alcohol_level, drowsy_score, '
        'accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z) and 3 class labels (Safe, At-Risk, Danger). '
        'The model uses 80 decision trees with maximum depth of 8. Labels are assigned using rule-based '
        'logic based on sensor value thresholds for each hazard type.')

    add_table_caption(doc, "Table 6: ML Prediction Labels and Probabilities")
    make_table(doc,
        ["Demo Mode", "Predicted Class", "Safe %", "At-Risk %", "Danger %"],
        [
            ["Safe", "Safe", "92", "8", "0"],
            ["Risky", "At-Risk", "5", "92", "3"],
            ["Drunk", "Danger", "0", "5", "95"],
            ["Drowsy", "Danger", "0", "12", "88"],
            ["Crash", "Danger", "0", "0", "100"],
        ])
    add_body(doc,
        'In demo mode, predictions are deterministically aligned with the selected mode to ensure '
        'consistent demonstration behavior without contradictions.')

    add_sub_heading(doc, "7.5 Sensor Simulation Implementation")
    add_body(doc,
        'Each simulation mode generates sensor values within realistic ranges. The speedometer ranges '
        'from 30-50 km/h in safe mode to 85-95 km/h in risky mode. The alcohol sensor ranges from '
        '0.01-0.05 mg/L (safe) to 0.38-0.45 mg/L (drunk). The drowsiness tracker ranges from 0-15% '
        '(safe) to 82-94% (drowsy). Mechanical vibration ranges from 0.4-1.2 m/s² (safe) to 18.7 m/s² '
        '(crash impact). GPS coordinates simulate slow drift with coordinates frozen during crash events.')

    add_sub_heading(doc, "7.6 Simulation Modes")
    add_table_caption(doc, "Table 7: Simulation Mode Parameters")
    make_table(doc,
        ["Mode", "Speed", "Alcohol", "Drowsiness", "Vibration", "Prediction"],
        [
            ["Safe", "30-50 km/h", "0.01-0.05", "0-15%", "0.4-1.2 m/s²", "Safe"],
            ["Risky", "85-95 km/h", "0.04-0.11", "15-28%", "1.8-3.5 m/s²", "At-Risk"],
            ["Drunk", "30-42 km/h", "0.38-0.45", "8-25%", "0.8-2.2 m/s²", "Danger"],
            ["Drowsy", "52-60 km/h", "0.00-0.04", "82-94%", "0.6-1.6 m/s²", "Danger"],
            ["Crash", "72 to 0 km/h", "0.02", "5%", "18.7 m/s²", "Danger"],
        ])

    add_sub_heading(doc, "7.7 Emergency Alert Implementation")
    add_body(doc,
        'The emergency alert system activates when a crash event is detected. The crash sequence '
        'progresses over multiple ticks: Tick 0 shows normal riding at 72.4 km/h. Tick 1 simulates the '
        'impact event with speed dropping to 18.2 km/h, vibration spiking to 18.7 m/s², and accelerometer '
        'registering 5.2 G horizontal force. Tick 2+ shows the vehicle stopped at 0 km/h with impact '
        'readings persisting and the alert activated.')
    add_body(doc,
        'Upon crash detection, the system extracts GPS coordinates, generates a Google Maps URL, '
        'simulates SIM800L GSM SMS dispatch with crash details, and displays an emergency SOS card '
        'on the dashboard with severity, impact force, GPS coordinates, and GSM status.')

    add_sub_heading(doc, "7.8 Ignition Lock Explanation")
    add_body(doc,
        'The ignition lock feature prevents intoxicated riding by disabling the motorcycle starting system '
        'when unsafe alcohol levels are detected. When the MQ-3 sensor detects BAC above 0.35 mg/L, a '
        'relay module disconnects the ignition circuit. Important safety note: The lock prevents starting '
        'the motorcycle - it should never cut the engine of a moving motorcycle. In the current software '
        'prototype, this is simulated through the prediction display.')

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 8: MODULES DESCRIPTION
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 8: Modules Description")

    modules = [
        ("8.1 Sensor Monitoring System",
         "The foundational module managing collection and preprocessing of all sensor data. Generates "
         "10-dimensional sensor readings at 1-second intervals, maintains sensor value ranges appropriate "
         "to the selected simulation mode, provides GPS coordinate tracking with simulated drift, and "
         "manages transitions between sensor value profiles. Simulated sensors include MPU6050 "
         "Accelerometer/Gyroscope (6-axis), MQ-3 Alcohol Sensor, SW-420 Vibration Sensor, Speed Sensor, "
         "and IR Drowsiness Sensor."),
        ("8.2 AI/ML Risk Prediction Module",
         "The intelligence core analyzing sensor data and classifying rider condition using a trained "
         "Random Forest Classifier with 80 decision trees and maximum depth of 8. Processes a "
         "10-dimensional feature vector and outputs Safe, At-Risk, or Danger classification with "
         "per-class probability distributions. The trained model is serialized using joblib."),
        ("8.3 Alcohol Detection Module",
         "Monitors blood alcohol concentration using MQ-3 sensor simulation. Detection thresholds: "
         "Below 0.15 mg/L is Safe, 0.15-0.35 mg/L is At-Risk, above 0.35 mg/L is Danger. Response "
         "actions include dashboard warnings, Danger prediction status, and future ignition lock relay."),
        ("8.4 Drowsiness Detection Module",
         "Monitors rider fatigue level using eye blink pattern analysis simulation. The drowsiness score "
         "ranges from 0% to 100%. Below 50% is Safe, 50-75% is At-Risk, above 75% is Danger. Future "
         "hardware implementation includes a high-pitch buzzer alarm inside the helmet."),
        ("8.5 Crash and Impact Detection Module",
         "Analyzes accelerometer and vibration data to detect crash events. Detection criteria include "
         "vibration exceeding 12.0 m/s², accelerometer exceeding 4.0 G, or combined speed above 40 km/h "
         "with vibration above 8.0 m/s². The crash sequence simulates pre-crash, impact, and post-crash "
         "phases with automatic emergency alert activation."),
        ("8.6 GPS Location Tracking Module",
         "Provides real-time geographic coordinates. Currently simulated with base coordinates at "
         "Bengaluru, India (12.9716°N, 77.5946°E) with slow drift for movement simulation. Coordinates "
         "are frozen upon crash detection. Generates direct Google Maps URLs for location visualization."),
        ("8.7 GSM Emergency SMS Alert Module",
         "Handles dispatch of emergency notifications upon crash detection. Currently simulated with SMS "
         "content generation including crash severity, impact force, GPS coordinates, Google Maps URL, "
         "and timestamp. Future implementation uses SIM800L GSM module with AT command protocol."),
        ("8.8 React Live Dashboard Module",
         "Primary user interface for real-time monitoring. Components include mode selector panel, "
         "AI prediction card, six sensor telemetry cards, two historical trend charts (Recharts), "
         "emergency SOS card, and GPS coordinates display. Polls backend every second for fresh data."),
        ("8.9 Data Logging and Charts Module",
         "Manages historical sensor data storage and visualization. Maintains a rolling window of 20 "
         "sensor readings with timestamps. Pre-populates history with realistic trends when mode changes. "
         "Renders speed and vibration area charts with smooth animations."),
        ("8.10 Future Hardware Integration Module",
         "Outlines the planned architecture for transitioning to physical hardware. Pipeline: Helmet "
         "Sensors -> ESP32 (I2C, Analog, Digital) -> Wi-Fi -> FastAPI Backend -> ML Prediction -> React "
         "Dashboard. NEO-6M GPS via UART, SIM800L GSM via UART, Active Buzzer via GPIO, Relay Module "
         "via GPIO for ignition lock."),
    ]

    for title, desc in modules:
        # Custom compact subheading for Chapter 8
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.bold = True
        run.font.size = Pt(12)
        run.font.name = "Times New Roman"

        # Custom compact body paragraph for Chapter 8
        p = doc.add_paragraph()
        fmt = p.paragraph_format
        fmt.first_line_indent = Cm(1.27)
        fmt.space_after = Pt(3)
        fmt.line_spacing = 1.15
        run = p.add_run(desc)
        run.font.size = Pt(12)
        run.font.name = "Times New Roman"

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 9: OUTPUT AND SCREENSHOTS
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 9: Output and Screenshots")

    add_body(doc,
        'This chapter presents the output screenshots captured from the AI-Powered Smart Helmet web application, '
        'demonstrating the various features, interface views, and simulation modes.')

    screenshots = [
        ("Fig. 7: Home Page of Smart Helmet Website", "home_page.png",
         "The Home page displays the project title, abstract, navigation buttons, problem definition, "
         "monitoring modules overview, project highlights, team details, and future hardware integration information. "
         "The design uses a professional dark UI design with red-gold accent colors."),
        ("Fig. 8: Project Team Section", "project_team.png",
         "Team member cards with role-based icons (Brain for AI, CPU for IoT, Server for Backend), "
         "member names, and contribution badges. College name displayed prominently."),
        ("Fig. 9: Live Dashboard in Safe Mode", "live_dashboard_safe.png",
         "All sensor values within normal ranges. The AI prediction panel clearly shows RIDER STATE: SAFE "
         "with green styling, speed between 30-50 km/h, negligible alcohol, drowsiness below 15%."),
        ("Fig. 10: Risky Mode Showing At-Risk Prediction", "live_dashboard_risky.png",
         "Elevated speed (85-95 km/h). The AI prediction panel clearly shows RIDER STATE: AT-RISK "
         "with amber styling, sensor values indicate overspeeding behavior."),
        ("Fig. 11: Drunk Mode Showing Alcohol Detection", "live_dashboard_drunk.png",
         "Alcohol sensor shows elevated readings (0.38-0.45 mg/L). The AI prediction panel clearly shows "
         "RIDER STATE: DANGER with red styling, alcohol detection warning message displayed."),
        ("Fig. 12: Drowsy Mode Showing Fatigue Warning", "live_dashboard_drowsy.png",
         "Drowsiness tracker shows high fatigue scores (82-94%). The AI prediction panel clearly shows "
         "RIDER STATE: DANGER with red styling, fatigue/drowsiness warning message displayed."),
        ("Fig. 13: Crash Mode Showing Emergency SOS Alert", "live_dashboard_crash.png",
         "The AI prediction panel clearly shows RIDER STATE: DANGER with red styling. Emergency SOS Alert "
         "card displayed prominently with crash severity (Critical), impact force (5.2 G / 18.7 m/s²), "
         "GPS coordinates, Google Maps link, and GSM status (Sent)."),
        ("Fig. 14: GPS Location and Google Maps Link", "gps_location.png",
         "GPS section shows rider's latitude and longitude with a direct clickable Google Maps link."),
        ("Fig. 15: Project Modules Page", "project_modules.png",
         "All eight project modules displayed with icons, descriptions, and technical specifications."),
        ("Fig. 16: Future Hardware Integration Diagram", "future_hardware.png",
         "Visual pipeline diagram showing the planned sensor-to-cloud architecture."),
        ("Fig. 17: FastAPI Documentation Page", "fastapi_docs.png",
         "The FastAPI interactive documentation (Swagger UI) displaying the REST API endpoints and data schemas."),
    ]

    for caption, img_file, desc in screenshots:
        img_path = os.path.join(ASSETS_DIR, img_file)
        # Compact image paragraph
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.paragraph_format.keep_with_next = True
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(5.5))
        
        # Compact caption paragraph
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(4)
        p_cap.paragraph_format.keep_with_next = True
        run_cap = p_cap.add_run(caption)
        run_cap.bold = True
        run_cap.italic = True
        run_cap.font.size = Pt(12)
        run_cap.font.name = "Times New Roman"
        
        # Compact body description paragraph
        p_desc = doc.add_paragraph()
        p_desc.paragraph_format.first_line_indent = Cm(1.27)
        p_desc.paragraph_format.space_after = Pt(8)
        p_desc.paragraph_format.line_spacing = 1.15
        run_desc = p_desc.add_run(desc)
        run_desc.font.size = Pt(12)
        run_desc.font.name = "Times New Roman"

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 10: TESTING
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 10: Testing")

    add_sub_heading(doc, "10.1 Testing Overview")
    add_body(doc,
        'The system was tested comprehensively to ensure correct functionality across all simulation '
        'modes, API endpoints, and dashboard components. Testing was performed using manual functional '
        'testing, API endpoint verification, and UI behavior validation.')

    add_sub_heading(doc, "10.2 Test Cases and Results")
    add_table_caption(doc, "Table 8: Test Cases and Results")
    make_table(doc,
        ["TC ID", "Test Scenario", "Input", "Expected Output", "Actual Output", "Status"],
        [
            ["TC-01", "Safe mode prediction", "Select Safe", "SAFE, Green, 30-50 km/h", "SAFE, Green, 30-50 km/h", "Pass"],
            ["TC-02", "Risky mode prediction", "Select Risky", "AT-RISK, Amber, 85-95 km/h", "AT-RISK, Amber, 85-95 km/h", "Pass"],
            ["TC-03", "Drunk mode prediction", "Select Drunk", "DANGER, Red, Alcohol 0.38+", "DANGER, Red, Alcohol 0.38+", "Pass"],
            ["TC-04", "Drowsy mode prediction", "Select Drowsy", "DANGER, Red, Drowsy 82%+", "DANGER, Red, Drowsy 82%+", "Pass"],
            ["TC-05", "Crash mode prediction", "Select Crash", "DANGER, SOS, Vibration 18.7", "DANGER, SOS, Vibration 18.7", "Pass"],
            ["TC-06", "Emergency SOS", "Crash after impact", "SOS card, GPS, GSM Sent", "SOS card, GPS, GSM Sent", "Pass"],
            ["TC-07", "GPS link", "Click Maps link", "Opens Google Maps", "Opens Google Maps", "Pass"],
            ["TC-08", "API live-data", "GET /api/live-data", "JSON with sensor data", "JSON with sensor data", "Pass"],
            ["TC-09", "API alert", "GET /api/alert", "Alert details JSON", "Alert details JSON", "Pass"],
            ["TC-10", "API mode switch", "POST demo mode endpoint", "200 OK, mode updated", "200 OK, mode updated", "Pass"],
            ["TC-11", "Dashboard render", "Open dashboard", "All cards render", "All cards render", "Pass"],
            ["TC-12", "Mode switch speed", "Rapid switch", "Immediate update", "Immediate update", "Pass"],
        ])

    add_sub_heading(doc, "10.3 Testing Summary")
    add_body(doc,
        'All 12 test cases passed successfully. The system demonstrates consistent behavior across '
        'all simulation modes with predictions accurately matching the selected mode. API endpoints '
        'respond correctly and the dashboard renders all components without errors.')

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 11: ADVANTAGES AND APPLICATIONS
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 11: Advantages and Applications")

    add_sub_heading(doc, "11.1 Advantages")
    add_bullet(doc, "Improved Rider Safety: Continuous real-time monitoring of multiple rider parameters enables proactive identification of dangerous conditions.")
    add_bullet(doc, "Reduced Emergency Response Delay: Automatic crash detection and GPS-based SOS alerts eliminate dependency on bystander reporting.")
    add_bullet(doc, "Alcohol and Drowsiness Detection: Addresses two major causes of motorcycle accidents with real-time warnings.")
    add_bullet(doc, "AI-Based Risk Prediction: Random Forest ML model provides nuanced risk assessment with confidence probabilities.")
    add_bullet(doc, "GPS-Based Emergency Location: Direct Google Maps links ensure emergency responders can navigate to exact accident locations.")
    add_bullet(doc, "Useful for Smart Mobility Systems: Scalable architecture supports fleet management and centralized safety monitoring.")

    add_sub_heading(doc, "11.2 Applications")
    add_bullet(doc, "Motorcycle rider safety for daily commutes and long-distance travel.")
    add_bullet(doc, "Delivery rider safety for food delivery and courier companies.")
    add_bullet(doc, "Industrial helmet safety for construction, mining, and manufacturing environments.")
    add_bullet(doc, "Fleet monitoring and management for transportation companies.")
    add_bullet(doc, "Road safety research for studying riding patterns and accident causes.")
    add_bullet(doc, "College IoT/AI project demonstration for academic purposes.")

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 12: LIMITATIONS
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 12: Limitations")

    add_bullet(doc, "Current version uses simulated sensor data rather than real hardware sensors.")
    add_bullet(doc, "Real sensors (MPU6050, MQ-3, SW-420, NEO-6M) are not yet connected; hardware integration is planned as future scope.")
    add_bullet(doc, "SMS alert is simulated; no actual GSM SMS transmission through cellular network.")
    add_bullet(doc, "ML model trained on synthetic data; real-world accuracy may differ.")
    add_bullet(doc, "Accuracy depends on real sensor quality, calibration, and reliability in future hardware implementation.")
    add_bullet(doc, "Physical sensors require careful calibration for each specific helmet and riding environment.")
    add_bullet(doc, "Internet/network dependency for communication between sensor module and backend server.")
    add_bullet(doc, "Current system monitors a single rider; multi-rider fleet monitoring requires architectural modifications.")
    add_bullet(doc, "No dedicated mobile application; dashboard is web-based only.")
    add_bullet(doc, "Power consumption management needed for battery-operated hardware in future implementation.")

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 13: FUTURE SCOPE
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 13: Future Scope")

    add_bullet(doc, "Real helmet hardware integration with embedded sensors in the helmet cavity.")
    add_bullet(doc, "ESP32/Arduino integration with firmware for sensor collection and Wi-Fi communication.")
    add_bullet(doc, "Real-time GPS tracking using NEO-6M GPS module with satellite-based coordinates.")
    add_bullet(doc, "Actual GSM SMS alert dispatch using SIM800L module with cellular network.")
    add_bullet(doc, "Cloud database integration (Firebase, AWS, GCP) for persistent data logging.")
    add_bullet(doc, "Mobile application development for iOS and Android with push notifications.")
    add_bullet(doc, "Real accident dataset training for improved ML model accuracy.")
    add_bullet(doc, "Hospital and emergency service integration for automated emergency dispatch.")
    add_bullet(doc, "Ignition lock using relay module to prevent intoxicated riding.")
    add_bullet(doc, "Voice alert and buzzer system inside the helmet for immediate rider feedback.")
    add_bullet(doc, "Helmet wearing detection using pressure or proximity sensors.")
    add_bullet(doc, "Battery-powered compact PCB design for all electronic components.")

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 14: CONCLUSION
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 14: Conclusion")

    add_body(doc,
        'The AI-Powered Smart Helmet with Accident Prediction and Emergency Alert System successfully '
        'demonstrates the integration of Artificial Intelligence, Internet of Things, and modern web '
        'technologies to address the critical problem of motorcycle rider safety.')
    add_body(doc,
        'Through this mini project, we have developed a 50% working software prototype that showcases '
        'the complete data pipeline - from sensor data acquisition (simulated) to AI-based risk prediction '
        'using a Random Forest Classifier, and finally to emergency alert dispatch simulation with GPS '
        'coordinates.')
    add_body(doc,
        'The key achievements include: A Random Forest Classifier trained on a 10-dimensional sensor '
        'feature space capable of classifying rider conditions into three risk levels. A professional-grade '
        'full-stack web application with FastAPI backend and React.js frontend. Five distinct simulation '
        'modes demonstrating the system response to different rider conditions. An automated crash '
        'detection and emergency response system with GPS and Google Maps integration. A modular '
        'architecture designed for seamless transition to physical hardware.')
    add_body(doc,
        'The project validates the concept that an intelligent helmet system can significantly improve '
        'motorcycle rider safety by providing continuous monitoring, proactive risk prediction, and '
        'automated emergency response. The software prototype serves as a solid foundation for future '
        'hardware development using ESP32 microcontrollers and the planned sensor suite.')
    add_body(doc,
        'This project has provided valuable hands-on experience in full-stack web development, Machine '
        'Learning model training and deployment, REST API design, real-time telemetry visualization, and system '
        'architecture design - skills directly applicable to professional software engineering and IoT '
        'development careers.')

    # ═══════════════════════════════════════════════════════════════
    #  CHAPTER 15: REFERENCES
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Chapter 15: References / Bibliography")

    refs = [
        "FastAPI - Modern, Fast Web Framework for Building APIs with Python 3.7+. Official Documentation. https://fastapi.tiangolo.com/",
        "React - A JavaScript Library for Building User Interfaces. Official Documentation. https://react.dev/",
        "Vite - Next Generation Frontend Tooling. Official Documentation. https://vitejs.dev/",
        "Scikit-learn - Machine Learning in Python. Official Documentation. https://scikit-learn.org/",
        "NumPy - The Fundamental Package for Scientific Computing with Python. https://numpy.org/",
        "Pandas - Python Data Analysis Library. https://pandas.pydata.org/",
        "Recharts - A Composable Charting Library Built on React Components. https://recharts.org/",
        'World Health Organization (WHO), "Global Status Report on Road Safety," 2023.',
        'National Crime Records Bureau (NCRB), Ministry of Home Affairs, Government of India, "Accidental Deaths and Suicides in India," Annual Report.',
        'InvenSense Inc., "MPU-6050 Six-Axis MEMS MotionTracking Device," Product Datasheet.',
        'Zhengzhou Winsen Electronics, "MQ-3 Semiconductor Sensor for Alcohol Detection," Technical Datasheet.',
        'U-blox AG, "NEO-6M GPS Module," Product Datasheet and Integration Manual.',
        'SIMCom Wireless Solutions, "SIM800L GSM/GPRS Module," Hardware Design Guide.',
        "Espressif Systems, ESP32 Technical Reference Manual. https://www.espressif.com/",
        "General references on IoT-based accident detection, smart helmets, drowsiness detection, and alcohol detection.",
    ]

    for i, ref in enumerate(refs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-1.27)
        run = p.add_run(f"[{i}] {ref}")
        run.font.size = Pt(11)
        run.font.name = "Times New Roman"

    # ═══════════════════════════════════════════════════════════════
    #  APPENDIX A: BACKEND API DETAILS
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Appendix A: Backend API Details")

    add_table_caption(doc, "API Endpoints Summary")
    make_table(doc,
        ["Method", "Endpoint", "Description"],
        [
            ["GET", "/api/live-data", "Returns sensor data, prediction, history, mode"],
            ["GET", "/api/alert", "Returns emergency alert status and details"],
            ["POST", "/api/demo-mode", "Switches simulation mode"],
            ["POST", "/api/reset-alert", "Resets alert, returns to safe mode"],
        ])

    add_sub_heading(doc, "A.1 GET /api/live-data Response Example")
    add_code_block(doc, '{\n  "demo_mode": "safe",\n  "sensor_data": {\n    "speed": 42.3,\n    "vibration": 0.87,\n    "alcohol_level": 0.023,\n    "drowsy_score": 0.082,\n    "accel_x": 0.05, "accel_y": -0.03, "accel_z": 1.02,\n    "gyro_x": 1.4, "gyro_y": -0.8, "gyro_z": 2.1,\n    "latitude": 12.9716, "longitude": 77.5946\n  },\n  "prediction": {\n    "status": "Safe",\n    "class_probabilities": {"Safe": 0.92, "At-Risk": 0.08, "Danger": 0.0}\n  },\n  "history": [...],\n  "alert_active": false\n}')

    add_sub_heading(doc, "A.2 GET /api/alert Response Example (Crash Active)")
    add_code_block(doc, '{\n  "is_active": true,\n  "severity": "Critical",\n  "impact_force": "5.2 G (Horizontal) / 18.7 Vibration",\n  "timestamp": "2025-01-15 14:32:18",\n  "latitude": 12.9716, "longitude": 77.5946,\n  "gsm_status": "Sent"\n}')

    # ═══════════════════════════════════════════════════════════════
    #  APPENDIX B: IMPORTANT CODE SNIPPETS
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Appendix B: Important Code Snippets")

    add_sub_heading(doc, "B.1 Random Forest Model Training (model.py)")
    add_code_block(doc, 'def train_model():\n    df = generate_synthetic_data(1500)\n    X = df.drop(columns=["label"])\n    y = df["label"]\n    X_train, X_test, y_train, y_test = train_test_split(\n        X, y, test_size=0.2, random_state=42\n    )\n    model = RandomForestClassifier(\n        n_estimators=80, max_depth=8, random_state=42\n    )\n    model.fit(X_train, y_train)\n    joblib.dump(model, MODEL_PATH)\n    return model')

    add_sub_heading(doc, "B.2 Prediction Function (model.py)")
    add_code_block(doc, 'def predict_status(sensor_data: dict) -> dict:\n    feature_names = [\n        "speed", "vibration", "alcohol_level", "drowsy_score",\n        "accel_x", "accel_y", "accel_z",\n        "gyro_x", "gyro_y", "gyro_z"\n    ]\n    features = [float(sensor_data.get(name, 0.0))\n                for name in feature_names]\n    features_arr = np.array([features])\n    prediction = model.predict(features_arr)[0]\n    probabilities = model.predict_proba(features_arr)[0]\n    status_map = {0: "Safe", 1: "At-Risk", 2: "Danger"}\n    return {\n        "status": status_map[prediction],\n        "class_probabilities": {\n            "Safe": float(probabilities[0]),\n            "At-Risk": float(probabilities[1]),\n            "Danger": float(probabilities[2])\n        }\n    }')

    add_sub_heading(doc, "B.3 FastAPI Live Data Endpoint (main.py)")
    add_code_block(doc, '@app.get("/api/live-data")\ndef get_live_data():\n    with state.lock:\n        return {\n            "demo_mode": state.demo_mode,\n            "sensor_data": state.sensor_data,\n            "prediction": state.prediction,\n            "history": state.history,\n            "alert_active": state.alert_active\n        }')

    add_sub_heading(doc, "B.4 Frontend API Layer (api.js)")
    add_code_block(doc, "const BASE_URL = 'http://127.0.0.1:8080';\n\nexport async function fetchLiveData() {\n    const res = await fetch(`${BASE_URL}/api/live-data`);\n    return res.json();\n}\n\nexport async function setDemoMode(mode) {\n    const res = await fetch(`${BASE_URL}/api/demo-mode`, {\n        method: 'POST',\n        headers: { 'Content-Type': 'application/json' },\n        body: JSON.stringify({ mode })\n    });\n    return res.json();\n}")

    # ═══════════════════════════════════════════════════════════════
    #  APPENDIX C: RUN COMMANDS
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Appendix C: Run Commands")

    add_sub_heading(doc, "C.1 Backend Setup and Run")
    add_code_block(doc, "cd backend\npython -m venv .venv\n.venv\\Scripts\\activate\npip install -r requirements.txt\nuvicorn main:app --reload --port 8080")
    add_body(doc, "Backend API documentation (Swagger UI) available at: http://127.0.0.1:8080/docs")

    add_sub_heading(doc, "C.2 Frontend Setup and Run")
    add_code_block(doc, "cd frontend\nnpm install\nnpm run dev")
    add_body(doc, "Frontend application available at: http://localhost:5174/")

    # ═══════════════════════════════════════════════════════════════
    #  APPENDIX D: DEMO FLOW
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Appendix D: Demo Flow")

    demo_steps = [
        "Open Home Page - Explain the project title, abstract, and problem definition.",
        "Scroll to Project Team - Show team members, contribution badges, and college affiliation.",
        "Scroll to Hardware Integration - Walk through the planned sensor-to-cloud architecture.",
        "Navigate to Live Dashboard - Point out the prototype badge and simulation disclaimer.",
        "Start in Safe Mode - Show green SAFE prediction with stable sensor values.",
        "Switch to Risky Mode - Highlight amber AT-RISK state with elevated speed.",
        "Switch to Drunk Mode - Show DANGER state with alcohol detection warning.",
        "Switch to Drowsy Mode - Demonstrate fatigue warning and drowsiness alerts.",
        "Switch to Crash Mode - Showcase emergency SOS card, GPS, Google Maps link, GSM dispatch.",
        "Reset to Safe Mode - Confirm real-time mode switching capability.",
        "Navigate to Modules Page - Walk through all 8 project modules.",
        "Open Swagger Docs (http://127.0.0.1:8080/docs) - Demonstrate live API endpoints.",
    ]

    for i, step in enumerate(demo_steps, 1):
        add_body_no_indent(doc, f"{i}. {step}")

    # ═══════════════════════════════════════════════════════════════
    #  APPENDIX E: HARDWARE COMPONENTS LIST
    # ═══════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_chapter_heading(doc, "Appendix E: Hardware Components List")

    add_body(doc,
        'The following table lists the hardware components planned for future physical prototype '
        'implementation. The current software prototype uses simulated sensor data.')

    make_table(doc,
        ["S.No.", "Component", "Specification", "Qty", "Purpose"],
        [
            ["1", "ESP32 DevKit V1", "Dual-core 240MHz, Wi-Fi+BLE", "1", "Central microcontroller"],
            ["2", "MPU6050 Module", "6-axis MEMS accel+gyro", "1", "Impact/orientation detection"],
            ["3", "MQ-3 Sensor", "Semiconductor alcohol sensor", "1", "Breath alcohol detection"],
            ["4", "SW-420 Sensor", "Normally closed vibration", "1", "Mechanical impact detection"],
            ["5", "NEO-6M GPS", "50-channel GPS, UART", "1", "Real-time location tracking"],
            ["6", "SIM800L Module", "Quad-band GSM/GPRS", "1", "SMS emergency dispatch"],
            ["7", "Active Buzzer", "5V piezoelectric", "1", "Audible warning alerts"],
            ["8", "5V Relay Module", "Optocoupler isolated", "1", "Ignition lock control"],
            ["9", "IR Sensor", "Infrared proximity", "1", "Eye blink/drowsiness"],
            ["10", "Li-Po Battery", "3.7V, 2000mAh", "1", "Power supply"],
            ["11", "Voltage Regulator", "AMS1117 3.3V", "1", "Power regulation"],
            ["12", "Helmet", "ISI-certified full-face", "1", "Physical housing"],
            ["13", "Jumper Wires", "M-M, M-F assorted", "Set", "Sensor connections"],
            ["14", "Breadboard", "830-point", "1", "Prototyping connections"],
            ["15", "USB Cable", "Micro-USB", "1", "Programming and power"],
        ])

    doc.save(OUTPUT_DOCX)
    print(f"[OK] Saved DOCX to {OUTPUT_DOCX}")


if __name__ == "__main__":
    page_map = {}
    if os.path.exists(PAGE_MAP_FILE):
        try:
            with open(PAGE_MAP_FILE, "r") as f:
                page_map = json.load(f)
            print(f"[INFO] Loaded existing page map with {len(page_map)} entries.")
        except Exception as e:
            print(f"[WARN] Could not load page map: {e}")
            
    build_report(page_map)
