# -*- coding: utf-8 -*-
"""Builds the upgrade plan for "Diamond in the Crown" (Yud-Tes Kislev 5787) as an RTL docx."""
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "Arial"
GOLD = RGBColor(0x9A, 0x6B, 0x00)
NAVY = RGBColor(0x1B, 0x2A, 0x4A)

doc = Document()
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Cm(2)
sec.top_margin = sec.bottom_margin = Cm(1.8)
sec._sectPr.append(OxmlElement("w:bidi"))

st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:cs"), FONT)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)


def _rtl_par(p):
    pPr = p._p.get_or_add_pPr()
    b = OxmlElement("w:bidi")
    pPr.insert(0, b)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def _run(p, text, bold=False, size=None, color=None, ltr=False, italic=False):
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.name = FONT
    rPr = r._r.get_or_add_rPr()
    rPr.rFonts.set(qn("w:cs"), FONT)
    if not ltr:
        rPr.append(OxmlElement("w:rtl"))
    if bold:
        rPr.append(OxmlElement("w:bCs"))
    if size:
        r.font.size = Pt(size)
        szcs = OxmlElement("w:szCs")
        szcs.set(qn("w:val"), str(int(size * 2)))
        rPr.append(szcs)
    if color:
        r.font.color.rgb = color
    return r


def para(text="", bold=False, size=None, color=None, space_after=4, ltr=False, center=False, italic=False):
    p = doc.add_paragraph()
    if ltr:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    else:
        _rtl_par(p)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    # support **bold** segments
    parts = text.split("**")
    for i, part in enumerate(parts):
        if part:
            _run(p, part, bold=bold or (i % 2 == 1), size=size, color=color, ltr=ltr, italic=italic)
    return p


def h1(text):
    p = para(text, bold=True, size=16, color=NAVY, space_after=6)
    p.paragraph_format.space_before = Pt(14)
    return p


def h2(text):
    p = para(text, bold=True, size=13, color=GOLD, space_after=4)
    p.paragraph_format.space_before = Pt(8)
    return p


def bullet(text):
    return para("•  " + text, space_after=2)


def _shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def table(header, rows, widths=None, ltr_cols=()):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    tblPr = t._tbl.tblPr
    tblPr.append(OxmlElement("w:bidiVisual"))
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        p = c.paragraphs[0]
        _rtl_par(p)
        _run(p, h, bold=True, size=10, color=RGBColor(0xFF, 0xFF, 0xFF))
        _shade(c, "1B2A4A")
    for r_i, row in enumerate(rows):
        cells = t.add_row().cells
        for i, val in enumerate(row):
            c = cells[i]
            c.text = ""
            lines = str(val).split("\n")
            for li, line in enumerate(lines):
                p = c.paragraphs[0] if li == 0 else c.add_paragraph()
                if i in ltr_cols:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                else:
                    _rtl_par(p)
                parts = line.split("**")
                for k, part in enumerate(parts):
                    if part:
                        _run(p, part, bold=(k % 2 == 1), size=9.5, ltr=(i in ltr_cols))
            if r_i % 2 == 1:
                _shade(c, "F4EFE3")
    if widths:
        t.autofit = False
        for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), widths):
            gc.set(qn("w:w"), str(int(w * 567)))
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def code_box(text):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    c = t.rows[0].cells[0]
    _shade(c, "F2F2F2")
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    _run(p, text, size=9, ltr=True)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)




def image(path, width_cm=16, caption=None):
    from docx.shared import Cm as _Cm
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=_Cm(width_cm))
    if caption:
        para(caption, size=9, center=True, space_after=8)


def page_break():
    from docx.enum.text import WD_BREAK
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
