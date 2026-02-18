import tempfile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime


def generate_pdf(data):

    pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    doc = SimpleDocTemplate(pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = []

    # TITLE 
    elems.append(Paragraph(
        "<b>LINE BALANCING SIMULATION REPORT</b>",
        styles["Title"]
    ))
    elems.append(Spacer(1, 12))
    elems.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"]
    ))
    elems.append(Spacer(1, 20))

    # KEY METRICS
    elems.append(Paragraph("<b>KEY PERFORMANCE METRICS</b>", styles["Heading2"]))
    elems.append(Spacer(1, 8))

    m = [
        ["Target Output Rate (units/hr)", f"{data['target_rate']}"],
        ["Actual Output Rate (units/hr)", f"{data['actual_rate']:.2f}"],
        ["Cycle Time (min)", f"{data['cycle_time']}"],
        ["Number of Workstations", f"{data['stations']}"],
        ["Line Efficiency (%)", f"{data['efficiency']:.2f}"]
    ]

    mt = Table(m, colWidths=[3.5*inch, 2*inch])
    mt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica')
    ]))
    elems += [mt, Spacer(1, 20)]

    # WORKSTATION ALLOCATION 
    elems.append(Paragraph("<b>WORKSTATION ALLOCATION</b>", styles["Heading2"]))
    elems.append(Spacer(1, 8))

    alloc_df = data["alloc_df"]
    alloc_data = [alloc_df.columns.tolist()] + alloc_df.astype(str).values.tolist()

    at = Table(alloc_data, repeatRows=1)
    at.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('GRID', (0,0), (-1,-1), 0.8, colors.grey),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica')
    ]))
    elems += [at, Spacer(1, 20)]

    # GRAPH 
    elems.append(Paragraph("<b>WORKLOAD DISTRIBUTION</b>", styles["Heading2"]))
    elems.append(Spacer(1, 8))
    elems.append(Image(data["graph_path"], width=5*inch, height=3*inch))

    doc.build(elems)
    return pdf
