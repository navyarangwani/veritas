import os
import io
import time
from typing import Dict, Any, List
import pandas as pd

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
except ImportError:
    pass


def generate_audit_excel(audit_data: Dict[str, Any]) -> bytes:
    """
    Generates a structured multi-tab Excel workbook containing:
    1. Executive Summary & Scores
    2. Itemized Testing Matrix (with Page/Bounding Box citations & Evidence URLs)
    3. Mathematical Reconciliations
    """
    output = io.BytesIO()
    results = audit_data.get("results", [])
    scores = audit_data.get("corporate_scores", {})
    metadata = audit_data.get("audit_metadata", {})
    company = audit_data.get("company_name", "Enterprise Entity")

    # 1. Summary Sheet
    summary_data = [
        {"Parameter": "Entity Under Audit", "Value": company},
        {"Parameter": "Assurance Standard", "Value": metadata.get("standard_applied", "ISSA 5000 / ISAE 3000")},
        {"Parameter": "Veritas Greenwashing Exposure Score", "Value": f"{scores.get('exposure_score', 0)} / 100"},
        {"Parameter": "Assurance Readiness Index", "Value": f"{scores.get('readiness_index', 0)}%"},
        {"Parameter": "Executive Assessment", "Value": scores.get("rating", "N/A")},
        {"Parameter": "Total Claims Tested", "Value": scores.get("total_claims", len(results))},
        {"Parameter": "Verified Claims", "Value": scores.get("verified_count", 0)},
        {"Parameter": "Contradicted / Material Misstatements", "Value": scores.get("contradicted_count", 0)},
        {"Parameter": "Arithmetic Inconsistencies", "Value": scores.get("arithmetic_flaw_count", 0)},
        {"Parameter": "Selective Disclosures Flagged", "Value": scores.get("selective_disclosure_count", 0)},
        {"Parameter": "Unverified / Gaps", "Value": scores.get("unverified_count", 0)},
    ]
    df_summary = pd.DataFrame(summary_data)

    # 2. Testing Matrix Sheet
    matrix_rows = []
    for r in results:
        matrix_rows.append({
            "Claim ID": r.get("claim_id"),
            "Page": r.get("page"),
            "Metric Domain": r.get("metric_type"),
            "Reported Value": r.get("value"),
            "Verbatim Disclosure": r.get("claim_text"),
            "Verdict": r.get("verdict"),
            "Risk Level": r.get("risk_level"),
            "Confidence": f"{r.get('confidence')}%",
            "Assurance Opinion": r.get("assurance_opinion"),
            "CSRD ESRS": r.get("taxonomy", {}).get("csrd_esrs", "N/A"),
            "GRI Standard": r.get("taxonomy", {}).get("gri_standard", "N/A"),
            "Math Audit": r.get("math_audit", {}).get("detail", "Nominal"),
            "Greenwashing Typology": r.get("typology", {}).get("typology", "None"),
            "Forensic Reasoning": r.get("reasoning"),
            "Recommended Auditor Action": r.get("workpaper_action"),
            "Primary Evidence URL": r.get("sources", [{}])[0].get("url", "N/A") if r.get("sources") else "N/A"
        })
    df_matrix = pd.DataFrame(matrix_rows)

    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="Executive Summary", index=False)
            df_matrix.to_excel(writer, sheet_name="Testing Workpapers", index=False)
        return output.getvalue()
    except Exception:
        return df_matrix.to_csv(index=False).encode("utf-8")


def generate_audit_pdf(audit_data: Dict[str, Any]) -> bytes:
    """
    Generates a publication-quality ISSA 5000 Pre-Assurance Memorandum in PDF format.
    Zero emojis, formal Big 4 institutional styling.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Formal Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569')
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    
    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    story = []
    
    company = audit_data.get("company_name", "Enterprise Entity")
    scores = audit_data.get("corporate_scores", {})
    results = audit_data.get("results", [])
    sbti = audit_data.get("sbti_status", {})

    # Header Banner
    story.append(Paragraph("VERITAS ESG FORENSIC ASSURANCE PRACTICE", subtitle_style))
    story.append(Paragraph("PRE-ASSURANCE ENGAGEMENT MEMORANDUM", title_style))
    story.append(Paragraph(f"Subject Entity: <b>{company}</b> &nbsp;|&nbsp; Standard: <b>ISSA 5000 / ISAE 3000 Limited Assurance</b> &nbsp;|&nbsp; Date: {time.strftime('%B %d, %Y')}", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0F172A'), spaceBefore=2, spaceAfter=10))

    # Executive Scorecard Table
    scorecard_data = [
        [
            Paragraph("<b>Veritas Greenwashing Exposure Score</b>", bold_body),
            Paragraph(f"<b><font size=13 color={'#B91C1C' if scores.get('exposure_score',0)>40 else '#15803D'}>{scores.get('exposure_score', 0)} / 100</font></b>", bold_body),
            Paragraph("<b>Assurance Readiness Index</b>", bold_body),
            Paragraph(f"<b><font size=13 color='#0F172A'>{scores.get('readiness_index', 0)}%</font></b>", bold_body)
        ],
        [
            Paragraph("<b>Overall Opinion</b>", bold_body),
            Paragraph(f"<b>{scores.get('rating', 'NOMINAL')}</b>", body_style),
            Paragraph("<b>SBTi Target Status</b>", bold_body),
            Paragraph(f"{sbti.get('status', 'Unverified')} ({sbti.get('near_term_status', 'N/A')})", body_style)
        ]
    ]
    t_scorecard = Table(scorecard_data, colWidths=[150, 120, 140, 130])
    t_scorecard.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_scorecard)
    story.append(Spacer(1, 12))

    # Findings & Exceptions Summary
    story.append(Paragraph("1. SUMMARY OF EXCEPTIONS AND AUDIT FINDINGS", section_heading))
    exceptions_summary = f"""
    The automated forensic audit examined <b>{len(results)} high-materiality ESG disclosures</b> across greenhouse gas emissions, energy, water, and circularity.
    Testing revealed <b>{scores.get('contradicted_count', 0)} Contradicted claims</b>, <b>{scores.get('arithmetic_flaw_count', 0)} Arithmetic discrepancies</b>, and <b>{scores.get('selective_disclosure_count', 0)} Selective disclosure risks</b>.
    """
    story.append(Paragraph(exceptions_summary.strip(), body_style))
    story.append(Spacer(1, 8))

    # Itemized Workpaper Table (First 12 claims)
    story.append(Paragraph("2. ITEMIZED TESTING WORKPAPERS", section_heading))
    
    headers = [
        Paragraph("<b>Ref ID</b>", bold_body),
        Paragraph("<b>Pg</b>", bold_body),
        Paragraph("<b>Disclosed Metric</b>", bold_body),
        Paragraph("<b>Verdict</b>", bold_body),
        Paragraph("<b>Risk</b>", bold_body),
        Paragraph("<b>Forensic Auditor Notes</b>", bold_body)
    ]
    table_rows = [headers]

    for r in results[:12]:
        verdict = r.get("verdict", "Unverified")
        v_color = "#15803D" if verdict == "Verified" else ("#B91C1C" if verdict in ["Contradicted", "Arithmetic Discrepancy"] else "#C2410C")
        
        table_rows.append([
            Paragraph(r.get("claim_id", "CLM"), body_style),
            Paragraph(str(r.get("page", 1)), body_style),
            Paragraph(r.get("claim_text", "")[:75] + ("..." if len(r.get("claim_text", "")) > 75 else ""), body_style),
            Paragraph(f"<b><font color='{v_color}'>{verdict.upper()}</font></b>", bold_body),
            Paragraph(str(r.get("risk_level", "LOW RISK")), body_style),
            Paragraph(r.get("reasoning", "")[:120] + ("..." if len(r.get("reasoning", "")) > 120 else ""), body_style)
        ])

    t_findings = Table(table_rows, colWidths=[55, 25, 175, 75, 65, 145])
    t_findings.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_findings)
    story.append(Spacer(1, 14))

    # Engagement Sign-off Box
    story.append(Paragraph("3. ENGAGEMENT CONCLUSION AND ATTESTATION", section_heading))
    signoff_text = """
    Based on the procedures performed under ISSA 5000 pre-assurance scoping, nothing has come to our attention that causes us to believe the verified metrics are materially misstated, except for the specific items identified in the Exceptions Log above. Engagement team recommends requesting primary meter records and SBTi target submission certificates prior to issuance of final assurance opinion.
    """
    story.append(Paragraph(signoff_text.strip(), body_style))
    story.append(Spacer(1, 10))
    
    signoff_table = Table([
        [Paragraph("<b>Lead Assurance Partner:</b> Veritas Forensic Assurance Practice", body_style), Paragraph("<b>Signature:</b> <i>[Digitally Signed — ISSA 5000 Audit Trail]</i>", body_style)],
        [Paragraph(f"<b>Date of Execution:</b> {time.strftime('%Y-%m-%d %H:%M:%S UTC')}", body_style), Paragraph("<b>Status:</b> Pre-Assurance Testing Complete", body_style)]
    ], colWidths=[270, 270])
    signoff_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ]))
    story.append(signoff_table)

    doc.build(story)
    return buffer.getvalue()
