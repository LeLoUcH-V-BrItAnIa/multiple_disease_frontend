from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf_report(df, username, insights=None):
    file_path = f"{username}_health_report.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("🩺 Health Prediction Report", styles['Title']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"User: {username}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Summary
    elements.append(Paragraph(f"Total Records: {len(df)}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Disease Counts
    disease_counts = df['Disease'].value_counts().to_dict()
    elements.append(Paragraph("Disease Distribution:", styles['Heading2']))
    for d, c in disease_counts.items():
        elements.append(Paragraph(f"{d}: {c}", styles['Normal']))

    elements.append(Spacer(1, 12))

    # Result Counts
    result_counts = df['Result'].value_counts().to_dict()
    elements.append(Paragraph("Result Summary:", styles['Heading2']))
    for r, c in result_counts.items():
        elements.append(Paragraph(f"{r}: {c}", styles['Normal']))

    elements.append(Spacer(1, 12))

    # AI Insights (optional)
    if insights:
        elements.append(Paragraph("AI Insights:", styles['Heading2']))
        elements.append(Paragraph(insights, styles['Normal']))

    # Build PDF
    doc.build(elements)

    return file_path