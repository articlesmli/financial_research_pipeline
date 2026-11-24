import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(analysis_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=12
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = styles['Normal']

    # Title & Header
    ticker = analysis_data.get("ticker", "UNKNOWN")
    story.append(Paragraph(f"Investment Committee Report: {ticker}", title_style))
    story.append(Paragraph(f"Status: <b>{analysis_data.get('status')}</b> | Stance: <b>{analysis_data.get('stance')}</b> | Allocation: <b>{analysis_data.get('position_size_pct')}%</b>", body_style))
    story.append(Spacer(1, 12))

    # Quantitative Performance Table
    story.append(Paragraph("Quantitative Backtest Performance", section_style))
    perf = analysis_data.get("backtest_performance", {})
    
    table_data = [
        ["Metric", "Value"],
        ["Initial Capital", f"${perf.get('initial_capital', 0):,.2f}"],
        ["Final Portfolio Value", f"${perf.get('final_portfolio_value', 0):,.2f}"],
        ["Total Return", f"{perf.get('total_return_pct', 0):+.2f}%"],
        ["Sharpe Ratio", f"{perf.get('sharpe_ratio', 0):.2f}"],
        ["Sortino Ratio", f"{perf.get('sortino_ratio', 0):.2f}"],
        ["Calmar Ratio", f"{perf.get('calmar_ratio', 0):.2f}"],
        ["Max Drawdown", f"{perf.get('max_drawdown', 0):.2f}%"],
        ["95% Daily VaR", f"${perf.get('var_95', 0):,.2f}"],
        ["Hit Rate", f"{perf.get('hit_rate', 0):.2f}%"]
    ]
    
    t = Table(table_data, colWidths=[200, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#E2E8F0")),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor("#1A365D")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0"))
    ]))
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
