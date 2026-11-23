
from io import BytesIO
from datetime import date, datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


def generate_market_report(
    trend_data: dict,
    comparison_data: dict,
    start_date: date,
    end_date: date,
) -> bytes:

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Bitumen Market Intelligence Report",
        author="PPS Bitumen Intelligence - Demo",
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=19,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=12,
        spaceAfter=7,
    ))

    styles.add(ParagraphStyle(
        name="SmallNote",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.grey,
    ))

    story = []

    product_name = trend_data.get("product_name", "Bitumen")
    trend = trend_data.get("trend", "Insufficient Data")

    story.append(Paragraph(
        "BITUMEN MARKET INTELLIGENCE",
        styles["ReportTitle"]
    ))

    story.append(Paragraph(
        "Historical Market Trend & Supplier Analysis",
        styles["Heading3"]
    ))

    story.append(Spacer(1, 5))

    metadata = [
        ["Product", str(product_name)],
        ["Report Period", f"{start_date} to {end_date}"],
        ["Generated On", datetime.now().strftime("%d %B %Y, %I:%M %p")],
        ["Overall Trend", str(trend)],
    ]

    metadata_table = Table(metadata, colWidths=[42 * mm, 125 * mm])

    metadata_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF0F8")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#17365D")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    story.append(metadata_table)
    story.append(Spacer(1, 12))

    # Market movement summary

    story.append(Paragraph(
        "1. Market Movement Summary",
        styles["SectionHeading"]
    ))

    summary_rows = [
        ["Metric", "Value"],
        ["Rate Updates", str(trend_data.get("total_rate_updates", 0))],
        ["Opening Rate", f"Rs. {trend_data.get('opening_rate') or 0:,.2f}"],
        ["Latest Rate", f"Rs. {trend_data.get('latest_rate') or 0:,.2f}"],
        ["Average Rate", f"Rs. {trend_data.get('average_rate') or 0:,.2f}"],
        ["Minimum Rate", f"Rs. {trend_data.get('minimum_rate') or 0:,.2f}"],
        ["Maximum Rate", f"Rs. {trend_data.get('maximum_rate') or 0:,.2f}"],
        ["Price Movement", f"Rs. {trend_data.get('absolute_change') or 0:,.2f}"],
        ["Percentage Movement", f"{trend_data.get('percentage_change') or 0:.2f}%"],
    ]

    summary_table = Table(
        summary_rows,
        colWidths=[85 * mm, 82 * mm],
        repeatRows=1
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F3F6FA")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))

    story.append(summary_table)

    # Supplier comparison

    story.append(Paragraph(
        "2. Supplier Rate Comparison",
        styles["SectionHeading"]
    ))

    rates = comparison_data.get("rates", [])

    comparison_rows = [[
        "Supplier",
        "Rate",
        "Unit",
        "Effective Date",
        "Difference",
    ]]

    for item in rates:
        comparison_rows.append([
            str(item.get("supplier_name") or "Unknown"),
            f"Rs. {item.get('rate', 0):,.2f}",
            str(item.get("unit", "MT")),
            str(item.get("effective_date", "-")),
            f"Rs. {item.get('difference_from_lowest', 0):,.2f}",
        ])

    if len(comparison_rows) == 1:
        comparison_rows.append(["No data", "-", "-", "-", "-"])

    comparison_table = Table(
        comparison_rows,
        colWidths=[42 * mm, 30 * mm, 20 * mm, 38 * mm, 37 * mm],
        repeatRows=1
    )

    comparison_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F3F6FA")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    story.append(comparison_table)

    # Supplier movement

    story.append(Paragraph(
        "3. Supplier-wise Market Movement",
        styles["SectionHeading"]
    ))

    movement_rows = [[
        "Supplier",
        "Updates",
        "Opening",
        "Latest",
        "Change",
        "Trend",
    ]]

    for item in trend_data.get("supplier_movements", []):
        movement_rows.append([
            str(item.get("supplier_name", "Unknown")),
            str(item.get("total_rate_updates", 0)),
            f"{item.get('opening_rate', 0):,.0f}",
            f"{item.get('latest_rate', 0):,.0f}",
            f"{item.get('absolute_change', 0):,.0f}",
            str(item.get("trend", "-")),
        ])

    if len(movement_rows) == 1:
        movement_rows.append(["No data", "-", "-", "-", "-", "-"])

    movement_table = Table(
        movement_rows,
        colWidths=[38 * mm, 20 * mm, 27 * mm, 27 * mm, 25 * mm, 30 * mm],
        repeatRows=1
    )

    movement_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(movement_table)

    # Business observations

    story.append(Paragraph(
        "4. Business Observations",
        styles["SectionHeading"]
    ))

    total_updates = trend_data.get("total_rate_updates", 0)
    percentage = trend_data.get("percentage_change") or 0
    lowest_rate = comparison_data.get("lowest_rate")
    highest_rate = comparison_data.get("highest_rate")

    observations = []

    if total_updates:
        observations.append(
            f"A total of {total_updates} rate updates were recorded "
            f"during the selected reporting period."
        )

    if trend == "Increasing":
        observations.append(
            f"The recorded market rate increased by {percentage:.2f}% "
            "between the opening and latest observations."
        )
    elif trend == "Decreasing":
        observations.append(
            f"The recorded market rate decreased by {abs(percentage):.2f}% "
            "between the opening and latest observations."
        )
    elif trend == "Stable":
        observations.append(
            "The recorded opening and latest market rates remained stable."
        )
    else:
        observations.append(
            "There is insufficient historical data to determine market direction."
        )

    if lowest_rate is not None and highest_rate is not None:
        observations.append(
            f"The supplier comparison shows a lowest rate of "
            f"Rs. {lowest_rate:,.2f} and a highest rate of "
            f"Rs. {highest_rate:,.2f}."
        )

    for observation in observations:
        story.append(Paragraph(
            f"- {observation}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(
        width="100%",
        thickness=0.5,
        color=colors.lightgrey
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "Disclaimer: This report is generated from the records available "
        "in the PPS Bitumen Intelligence demonstration application. "
        "Sample/demo records are illustrative and must not be treated "
        "as verified live market quotations or official PPS data.",
        styles["SmallNote"]
    ))

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
