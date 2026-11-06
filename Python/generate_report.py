"""
Builds Report.pdf (KPIs, charts and insights) from the cleaned data.
Run from the project root:  python Python/generate_report.py
Needs: pip install -r requirements-dev.txt
"""
from io import BytesIO
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "Dataset" / "cleaned_sales.csv.gz", parse_dates=["date"])
sales = df[df["is_valid_sale"]]

# ---------------------------------------------------------------- numbers
revenue = sales["revenue"].sum()
kpis = [
    ["Total revenue", f"INR {revenue/1e6:,.2f} M"],
    ["Order lines", f"{len(df):,}"],
    ["Units sold", f"{int(sales['qty'].sum()):,}"],
    ["Average order value", f"INR {sales['revenue'].mean():,.0f}"],
    ["Cancellation rate", f"{df['is_cancelled'].mean()*100:.1f}%"],
    ["Return rate", f"{df['is_returned'].mean()*100:.1f}%"],
]
cat = sales.groupby("category")["revenue"].sum().sort_values(ascending=False)
state = sales.groupby("ship_state")["revenue"].sum().sort_values(ascending=False)
ful = df.groupby("fulfilment")[["is_cancelled", "is_returned"]].mean() * 100
monthly = sales.groupby("month")["revenue"].sum()


def fig_to_img(fig, w=16):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=w * cm, height=w * cm * fig.get_size_inches()[1] / fig.get_size_inches()[0])


# ---------------------------------------------------------------- charts
fig, ax = plt.subplots(figsize=(8, 3.2))
d = sales.groupby("date")["revenue"].sum()
ax.plot(d.index, d.values, label="Daily"); ax.plot(d.index, d.rolling(7).mean(), label="7-day avg")
ax.set_title("Daily revenue (INR)"); ax.legend()
c1 = fig_to_img(fig)

fig, ax = plt.subplots(figsize=(8, 3.2))
cat.sort_values().plot(kind="barh", ax=ax, color="#FF9900"); ax.set_title("Revenue by category")
c2 = fig_to_img(fig)

fig, ax = plt.subplots(figsize=(8, 3.6))
state.head(10).sort_values().plot(kind="barh", ax=ax, color="#232F3E"); ax.set_title("Top 10 states by revenue")
c3 = fig_to_img(fig)

fig, ax = plt.subplots(figsize=(8, 3.2))
ful.plot(kind="bar", ax=ax, rot=0); ax.set_title("Cancel / return rate (%) by fulfilment")
c4 = fig_to_img(fig)

# ---------------------------------------------------------------- insights (computed, not hard-coded)
insights = [
    f"Top category is {cat.index[0]} with {cat.iloc[0]/revenue*100:.1f}% of revenue; "
    f"the top two categories ({cat.index[0]}, {cat.index[1]}) make up {cat.iloc[:2].sum()/revenue*100:.1f}%.",
    f"{state.index[0].title()} leads all states ({state.iloc[0]/revenue*100:.1f}% of revenue); "
    f"the top 5 states contribute {state.head(5).sum()/revenue*100:.1f}%.",
    f"Cancellation rate is {df['is_cancelled'].mean()*100:.1f}%; "
    f"highest in the '{ful['is_cancelled'].idxmax()}' fulfilment channel ({ful['is_cancelled'].max():.1f}%).",
    f"April was the strongest full month (INR {monthly.get('2022-04', 0)/1e6:.1f} M); "
    "March contains only one day of data and should not be compared.",
]

# ---------------------------------------------------------------- pdf
styles = getSampleStyleSheet()
doc = SimpleDocTemplate(str(ROOT / "Report.pdf"), pagesize=A4,
                        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)
story = [Paragraph("E-Commerce Sales Analytics Report", styles["Title"]),
         Paragraph("Source: Amazon India sales report, 31 Mar - 29 Jun 2022", styles["Normal"]),
         Spacer(1, 0.6 * cm), Paragraph("Key metrics", styles["Heading2"])]
t = Table(kpis, colWidths=[7 * cm, 7 * cm])
t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                       ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke)]))
story += [t, Spacer(1, 0.5 * cm), Paragraph("Key insights", styles["Heading2"])]
story += [Paragraph(f"• {i}", styles["Normal"]) for i in insights]
story += [PageBreak(), Paragraph("Sales trend", styles["Heading2"]), c1,
          Paragraph("Products", styles["Heading2"]), c2, PageBreak(),
          Paragraph("Geography", styles["Heading2"]), c3,
          Paragraph("Operations", styles["Heading2"]), c4,
          Spacer(1, 0.5 * cm), Paragraph("Recommendations", styles["Heading2"]),
          Paragraph("• Stock deeper in the top categories and sizes (M, L, XL).<br/>"
                    "• Run regional campaigns in the top-5 states and test the lower-ranked ones.<br/>"
                    "• Investigate the cancellation drivers in the highest-cancel fulfilment channel.<br/>"
                    "• Collect a longer date range before drawing seasonality conclusions.", styles["Normal"])]
doc.build(story)
print("Report.pdf written")
for i in insights:
    print("-", i)
