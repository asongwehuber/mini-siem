from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def create_table_pdf(title, headers, rows, filename):
    """
    Creates a simple table-based PDF.

    Parameters
    ----------
    title : str
        Report title.

    headers : list
        Table column names.

    rows : list[list]
        Table data.

    filename : str
        Output PDF filename.
    """

    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4)
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(title, styles["Title"])
    )

    elements.append(Spacer(1, 20))

    table_data = [headers]

    for row in rows:
        table_data.append(row)

    table = Table(table_data, repeatRows=1)

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),

            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )

    elements.append(table)

    doc.build(elements)