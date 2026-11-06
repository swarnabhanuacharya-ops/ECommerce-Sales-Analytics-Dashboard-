# Power BI Dashboard Guide

A `.pbix` file can only be created in Power BI Desktop (Windows). Follow these steps, then save it as
`PowerBI/Ecommerce_Dashboard.pbix` and export 3 screenshots into `Images/`.

## 1. Load data
Home > Get Data > Text/CSV > choose `Dataset/cleaned_sales.csv.gz` (unzip it first) or the raw CSV.
In Power Query: set `date` to Date, `amount` / `revenue` to Fixed decimal, remove `Unnamed: 22`.

## 2. DAX measures (Modeling > New measure)
```DAX
Total Revenue   = SUM(Sales[revenue])
Total Orders    = DISTINCTCOUNT(Sales[order_id])
Units Sold      = CALCULATE(SUM(Sales[qty]), Sales[is_valid_sale] = TRUE())
Avg Order Value = DIVIDE([Total Revenue], CALCULATE(COUNTROWS(Sales), Sales[is_valid_sale] = TRUE()))
Cancel Rate %   = DIVIDE(CALCULATE(COUNTROWS(Sales), Sales[is_cancelled] = TRUE()), COUNTROWS(Sales))
Return Rate %   = DIVIDE(CALCULATE(COUNTROWS(Sales), Sales[is_returned] = TRUE()), COUNTROWS(Sales))
Revenue 7D Avg  = AVERAGEX(DATESINPERIOD(Sales[date], MAX(Sales[date]), -7, DAY), [Total Revenue])
```
Create a Date table: `Calendar = CALENDARAUTO()` and relate it to `Sales[date]`.

## 3. Pages
| Page | Visuals |
|------|---------|
| 1 Overview | 6 KPI cards, daily revenue line, revenue by category donut, slicers: date, category, fulfilment |
| 2 Products | Top 15 styles bar, units by size column, category x size matrix with conditional formatting |
| 3 Geography & Ops | Filled map by `ship_state`, top cities bar, orders by status, cancel rate by fulfilment |

## 4. Finish
Use one theme (orange `#FF9900` + navy `#232F3E`), add titles, sync slicers across pages,
File > Save as `Ecommerce_Dashboard.pbix`, then File > Export > PDF if you want a copy.
Take 3 screenshots -> `Images/Dashboard1.png`, `Dashboard2.png`, `Dashboard3.png`.

> Power BI service dashboards cannot be embedded on Render for free; the Streamlit app in `app.py`
> is the live, deployable version of the same dashboard.
