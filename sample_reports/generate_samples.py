import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

os.makedirs("sample_reports", exist_ok=True)


def build_sample_pdf(filename: str, company: str, report_title: str, claims_text: str, table_data: list):
    filepath = os.path.join("sample_reports", filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#1A365D'))
    h2_style = ParagraphStyle('H2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#0F3822'), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#2D3748'))
    footnote_style = ParagraphStyle('Footnote', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, leading=10, textColor=colors.HexColor('#718096'))

    story = [
        Paragraph(company.upper(), ParagraphStyle('Comp', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#718096'))),
        Paragraph(report_title, title_style),
        Paragraph("Annual Sustainability & Statutory BRSR Disclosure — FY 2023-24", body_style),
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E0'), spaceBefore=2, spaceAfter=8),
        Paragraph("<b>1. Executive Sustainability Statement & Targets</b>", h2_style),
        Paragraph(claims_text, body_style),
        Spacer(1, 10),
        Paragraph("<b>2. Greenhouse Gas & Operational Energy Accounting Table</b>", h2_style)
    ]

    # Convert table strings to Paragraphs
    formatted_table = []
    for row_idx, row in enumerate(table_data):
        formatted_row = []
        for cell in row:
            if row_idx == 0:
                p = Paragraph(f"<b>{cell}</b>", ParagraphStyle('TH', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#1A202C')))
            else:
                p = Paragraph(str(cell), body_style)
            formatted_row.append(p)
        formatted_table.append(formatted_row)

    t = Table(formatted_table, colWidths=[200, 100, 100, 110])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))
    story.append(Paragraph("*Note: Scope 2 figures are calculated using market-based emission factors. Scope 3 excludes category 11 use of sold products.", footnote_style))
    story.append(Paragraph("†Restated: Baseline year adjusted to FY21 due to manufacturing consolidation.", footnote_style))

    doc.build(story)
    print(f"Created sample PDF at: {filepath}")


if __name__ == "__main__":
    # Sample 1: Tata Motors
    tata_text = """
    Tata Motors Limited is committed to achieving net-zero greenhouse gas emissions by 2045 for our commercial vehicle business.
    In FY 2023-24, we reduced our direct Scope 1 emissions by 18.2% from 420,000 tCO2e to 343,560 tCO2e.
    Renewable electricity sourcing reached 40.5% across all manufacturing operations in India and the UK.
    Total water recycled and reused amounted to 3,420 megaliters, accounting for 32% of total operational water withdrawal.
    """
    tata_table = [
        ["Emissions Metric", "FY 2021-22", "FY 2022-23", "FY 2023-24"],
        ["Scope 1 (Direct GHG) [tCO2e]", "440,000", "420,000", "343,560"],
        ["Scope 2 (Indirect Grid) [tCO2e]", "310,000", "295,000", "280,000"],
        ["Total Operational Scope 1+2 [tCO2e]", "750,000", "715,000", "623,560"],
        ["Renewable Energy Mix (%)", "24.0%", "31.5%", "40.5%"]
    ]
    build_sample_pdf("tata_motors_esg_sample.pdf", "Tata Motors Limited", "Sustainability & ESG Performance Report 2024", tata_text, tata_table)

    # Sample 2: Infosys
    infosys_text = """
    Infosys Limited has maintained carbon neutrality for the fifth consecutive year across Scope 1, Scope 2, and business travel.
    Our Science Based Targets initiative (SBTi) approved target commits to reducing absolute Scope 1 and 2 emissions 75% by 2030 from a 2020 baseline.
    In FY24, 67.2% of our total electricity consumption was sourced from renewable energy sources.
    Women represent 39.4% of our total global workforce, and female representation on the board stands at 33.3%.
    """
    infosys_table = [
        ["ESG Disclosures", "FY 2021-22", "FY 2022-23", "FY 2023-24"],
        ["Scope 1 Emissions [tCO2e]", "24,500", "21,200", "18,400"],
        ["Scope 2 (Market-based) [tCO2e]", "78,200", "62,100", "48,600"],
        ["Total Scope 1+2 GHG [tCO2e]", "102,700", "83,300", "67,000"],
        ["Renewable Energy Consumption (MWh)", "182,000", "215,000", "248,500"]
    ]
    build_sample_pdf("infosys_esg_sample.pdf", "Infosys Limited", "Environmental, Social & Governance (ESG) Report 2024", infosys_text, infosys_table)

    # Sample 3: High-Risk Greenwashing Case Study (Mathematical Discrepancy & Selective Disclosure)
    synthetic_text = """
    Apex Global Industries proudly announces that it has achieved complete Carbon Neutral operations in 2024 through our carbon offset program.
    We achieved a 45.0% reduction in Scope 1 emissions from 200,000 tCO2e in FY22 down to 150,000 tCO2e in FY24.
    Our total company carbon footprint is now only 210,000 tCO2e covering our corporate headquarters and domestic facilities.
    We planted 25,000 trees in our local biodiversity corridor, demonstrating our world-leading climate stewardship.
    """
    synthetic_table = [
        ["Emissions Metric", "FY 2021-22", "FY 2022-23", "FY 2023-24"],
        ["Scope 1 (Direct Facility) [tCO2e]", "200,000", "180,000", "150,000"],
        ["Scope 2 (Purchased Electricity) [tCO2e]", "90,000", "85,000", "80,000"],
        # NOTE: 150,000 + 80,000 = 230,000, but table falsely reports 210,000! Math engine should catch this!
        ["Total Operational GHG [tCO2e]", "290,000", "265,000", "210,000"],
        ["Carbon Offsets Retired [Credits]", "50,000", "100,000", "210,000"]
    ]
    build_sample_pdf("synthetic_greenwashing_audit_case.pdf", "Apex Global Industries", "Annual Climate & Sustainability Review 2024", synthetic_text, synthetic_table)
