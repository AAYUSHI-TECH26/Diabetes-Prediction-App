"""
Diabetes Report Generator — PDF using ReportLab
Generates professional patient reports with doctor verification stamp.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_report(record: dict, doctor_name: str) -> str:
    """Generate a PDF report and return its file path."""

    os.makedirs("reports", exist_ok=True)
    filename = f"reports/diabetes_report_{record['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4,
                            topMargin=1.5*cm, bottomMargin=1.5*cm,
                            leftMargin=2*cm, rightMargin=2*cm)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle("Title", parent=styles["Title"],
                                 fontSize=20, textColor=colors.HexColor("#1a3a5c"),
                                 spaceAfter=4, spaceBefore=0, alignment=TA_CENTER)
    sub_style   = ParagraphStyle("Sub", parent=styles["Normal"],
                                 fontSize=10, textColor=colors.HexColor("#5a6a7e"),
                                 alignment=TA_CENTER, spaceAfter=8)
    heading_style = ParagraphStyle("Heading", parent=styles["Normal"],
                                   fontSize=13, textColor=colors.HexColor("#1a3a5c"),
                                   fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=12)
    body_style  = ParagraphStyle("Body", parent=styles["Normal"],
                                 fontSize=10, spaceAfter=3)
    small_style = ParagraphStyle("Small", parent=styles["Normal"],
                                 fontSize=8.5, textColor=colors.HexColor("#666"))

    risk_level  = record.get("risk_level", "Unknown")
    prediction  = record.get("prediction", 0)
    risk_score  = record.get("risk_score", 0)
    verified    = record.get("doctor_verified", 0)
    doctor_notes = record.get("doctor_notes", "")

    # Risk color
    risk_color = {
        "Low Risk": colors.HexColor("#27ae60"),
        "Moderate Risk": colors.HexColor("#f39c12"),
        "High Risk": colors.HexColor("#e74c3c"),
        "Very High Risk": colors.HexColor("#8e44ad"),
    }.get(risk_level, colors.grey)

    story = []

    # ─── HEADER ────────────────────────────────────────────
    story.append(Paragraph("🩺 DIABETES PREDICTION REPORT", title_style))
    story.append(Paragraph("Powered by Ensemble ML | Pima Indian Dataset", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 10))

    # ─── PATIENT INFO ─────────────────────────────────────
    story.append(Paragraph("📋 Patient Information", heading_style))
    info_data = [
        ["Report ID:", f"#{record['id']}", "Date:", record.get("created_at","N/A")[:16]],
        ["Patient Name:", record.get("patient_name","N/A"), "Age:", f"{record.get('age','N/A')} years"],
        ["Assigned Doctor:", doctor_name, "Verified:", "✓ YES" if verified else "⏳ Pending"],
    ]
    info_table = Table(info_data, colWidths=[4.5*cm, 6.5*cm, 3*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f0f4f8")),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#f0f4f8"), colors.white]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#d0d8e4")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # ─── PREDICTION RESULT ────────────────────────────────
    story.append(Paragraph("🔬 Prediction Result", heading_style))

    result_bg = colors.HexColor("#fff3f3") if prediction else colors.HexColor("#f0fff4")
    result_text = "DIABETIC" if prediction else "NON-DIABETIC"

    result_data = [
        [f"Diagnosis: {result_text}",
         f"Risk Level: {risk_level}",
         f"Risk Score: {risk_score}%"]
    ]
    result_table = Table(result_data, colWidths=[6*cm, 6*cm, 6*cm])
    result_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 11),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (-1,-1), result_bg),
        ("TEXTCOLOR", (1,0), (1,0), risk_color),
        ("GRID", (0,0), (-1,-1), 1, risk_color),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [5]),
    ]))
    story.append(result_table)
    story.append(Spacer(1, 10))

    # ─── CLINICAL MEASUREMENTS ────────────────────────────
    story.append(Paragraph("📊 Clinical Measurements", heading_style))

    measurements = [
        ["Parameter", "Value", "Normal Range", "Status"],
        ["Pregnancies", str(record.get("pregnancies","N/A")), "N/A", "—"],
        ["Glucose (mg/dL)", str(record.get("glucose","N/A")), "70–100", "⚠" if float(record.get("glucose",0)) > 100 else "✓"],
        ["Blood Pressure (mmHg)", str(record.get("blood_pressure","N/A")), "< 80", "⚠" if float(record.get("blood_pressure",0)) > 80 else "✓"],
        ["Skin Thickness (mm)", str(record.get("skin_thickness","N/A")), "< 35", "—"],
        ["Insulin (μU/mL)", str(record.get("insulin","N/A")), "16–166", "—"],
        ["BMI (kg/m²)", str(record.get("bmi","N/A")), "< 25", "⚠" if float(record.get("bmi",0)) >= 25 else "✓"],
        ["Diabetes Pedigree", str(record.get("diabetes_pedigree","N/A")), "< 0.5", "⚠" if float(record.get("diabetes_pedigree",0)) > 0.5 else "✓"],
        ["Age (years)", str(record.get("age","N/A")), "—", "⚠" if float(record.get("age",0)) > 45 else "✓"],
    ]

    meas_table = Table(measurements, colWidths=[5.5*cm, 3.5*cm, 4*cm, 3*cm])
    meas_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a3a5c")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f9fc")]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#d0d8e4")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("ALIGN", (1,0), (3,-1), "CENTER"),
    ]))
    story.append(meas_table)
    story.append(Spacer(1, 10))

    # ─── DOCTOR NOTES ─────────────────────────────────────
    story.append(Paragraph("👨‍⚕️ Doctor's Assessment", heading_style))

    if verified and doctor_notes:
        notes_para = Paragraph(f"<b>Dr. {doctor_name} notes:</b><br/>{doctor_notes}", body_style)
    elif verified:
        notes_para = Paragraph(f"<b>Verified by Dr. {doctor_name}.</b> No additional notes.", body_style)
    else:
        notes_para = Paragraph("⏳ <b>Awaiting doctor verification.</b> Report will be updated once reviewed.", body_style)

    notes_box = Table([[notes_para]], colWidths=[17*cm])
    notes_box.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#fffde7") if verified else colors.HexColor("#fff3f3")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e0c060") if verified else colors.HexColor("#ffcccc")),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(notes_box)
    story.append(Spacer(1, 10))

    # ─── RECOMMENDATIONS ──────────────────────────────────
    story.append(Paragraph("💡 General Recommendations", heading_style))
    recs = []
    if prediction:
        recs = ["Consult an endocrinologist immediately",
                "Monitor blood glucose daily",
                "Follow a low-glycemic diet",
                "Exercise at least 150 min/week",
                "Consider HbA1c test every 3 months"]
    else:
        recs = ["Maintain a healthy diet and active lifestyle",
                "Annual glucose screening recommended",
                "Keep BMI below 25",
                "Avoid smoking and excessive alcohol",
                "Routine health checkup every 6 months"]

    rec_data = [[Paragraph(f"• {r}", body_style)] for r in recs]
    rec_table = Table(rec_data, colWidths=[17*cm])
    rec_table.setStyle(TableStyle([
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 15))

    # ─── FOOTER ────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3a5c")))
    footer_style = ParagraphStyle("Footer", parent=styles["Normal"],
                                  fontSize=8, textColor=colors.HexColor("#888"),
                                  alignment=TA_CENTER, spaceBefore=5)
    story.append(Paragraph(
        f"This report is generated by the AI Diabetes Prediction System using the Pima Indian Diabetes Dataset.<br/>"
        f"Report generated on {datetime.now().strftime('%d %B %Y at %H:%M')}.<br/>"
        f"<b>Disclaimer:</b> This is a decision-support tool. Always consult a qualified physician for diagnosis.",
        footer_style
    ))

    doc.build(story)
    return filename
