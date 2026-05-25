"""PDF 检测报告生成（fpdf2）"""

import io
from datetime import datetime

from fpdf import FPDF


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Semiconductor Epitaxial Thickness Test Report", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 9)
        self.cell(0, 6, "Multi-Beam Interference Correction System V1.0", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(4)


def _ascii_safe(text):
    """PDF 核心字体仅支持 Latin-1，中文等级转为英文描述"""
    mapping = {
        "强多光束干涉": "Strong multi-beam",
        "中等多光束干涉": "Moderate multi-beam",
        "弱/无多光束干涉": "Weak/none multi-beam",
    }
    s = str(text) if text is not None else "-"
    return mapping.get(s, s.encode("ascii", "replace").decode("ascii"))


def build_record_pdf(record: dict) -> bytes:
    """根据 film_record 字典生成 PDF 字节流"""
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "1. Specimen Information", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)

    rows = [
        ("Film Code", record.get("film_code", "-")),
        ("Material", record.get("material_type", "-")),
        ("Incident Angle", f"{record.get('theta_deg', '-')} deg"),
        ("Test Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    ]
    for label, val in rows:
        pdf.cell(50, 7, label + ":", border=0)
        pdf.cell(0, 7, str(val), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "2. Inversion Results", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)

    r2 = record.get("r_squared")
    status = "PASSED" if r2 and r2 > 0.8 else "REVIEW"
    result_rows = [
        ("Thickness (um)", record.get("thickness_um", "-")),
        ("R-squared", r2 if r2 is not None else "-"),
        ("Multi-beam Level", _ascii_safe(record.get("multi_beam_level", "-"))),
        ("Quality", status),
    ]
    for label, val in result_rows:
        pdf.cell(50, 7, label + ":", border=0)
        pdf.cell(0, 7, str(val), new_x="LMARGIN", new_y="NEXT")

    if record.get("notes"):
        pdf.ln(4)
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(0, 5, "Notes: " + str(record["notes"]))

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0, 4,
        "Auto-generated report for process reference. Results based on spectral interference inversion.",
    )

    buf = io.BytesIO()
    pdf.output(buf)
    return bytes(buf.getvalue())
