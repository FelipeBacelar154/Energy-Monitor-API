from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import cm
from sqlalchemy.orm import Session
from app.models.models import Equipment, Reading
from sqlalchemy import func

import base64
from io import BytesIO

COST_PER_KWH = 0.75


def generate_pdf(db: Session, output_path: str = None, chart_image: str = None):
    if not output_path:
        output_path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # TITLE
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20
    )

    elements.append(Paragraph("⚡ Energy Monitor - Report", title_style))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%d/%m/%Y at %H:%M')}",
        subtitle_style
    ))
    elements.append(Spacer(1, 0.5 * cm))

    # SUMMARY
    total_consumption = db.query(func.sum(Reading.consumption_kwh)).scalar() or 0
    total_cost = round(total_consumption * COST_PER_KWH, 2)
    total_equipments = db.query(Equipment).count()

    summary_data = [
        ['Total Equipments', 'Total Consumption', 'Estimated Cost'],
        [str(total_equipments), f"{round(total_consumption, 2)} kWh", f"R$ {total_cost}"]
    ]

    summary_table = Table(summary_data, colWidths=[5 * cm, 6 * cm, 6 * cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 1 * cm))

    # TABLE
    elements.append(Paragraph("Equipment Details", styles['Heading2']))
    elements.append(Spacer(1, 0.3 * cm))

    equipments = db.query(Equipment).all()

    table_data = [['Equipment', 'Power', 'Location', 'Consumption', 'Cost']]

    for eq in equipments:
        consumption = db.query(func.sum(Reading.consumption_kwh))\
            .filter(Reading.equipment_id == eq.id).scalar() or 0

        cost = round(consumption * COST_PER_KWH, 2)

        table_data.append([
            eq.name,
            str(eq.power_kw),
            eq.location,
            str(round(consumption, 2)),
            f"R$ {cost}"
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)

    # CHART
    if chart_image:
        elements.append(Spacer(1, 1 * cm))
        elements.append(Paragraph("Consumption Chart", styles['Heading2']))
        elements.append(Spacer(1, 0.3 * cm))

        image_data = chart_image.split(",")[1]
        image_bytes = base64.b64decode(image_data)

        image = Image(BytesIO(image_bytes))
        image.drawHeight = 8 * cm
        image.drawWidth = 16 * cm

        elements.append(image)

    doc.build(elements)
    return output_path