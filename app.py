"""
E-Commerce Sales Analytics Dashboard (Streamlit + Plotly)
Run locally:  streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="E-Commerce Sales Analytics", page_icon="🛒", layout="wide")

DATA = Path(__file__).parent / "Dataset" / "cleaned_sales.csv.gz"


@st.cache_data(show_spinner="Loading data...")
def load_data() -> pd.DataFrame:
    if not DATA.exists():  # first run on a fresh clone
        from Python.clean_data import clean
        df = clean()
        df.to_csv(DATA, index=False, compression="gzip")
    df = pd.read_csv(DATA, parse_dates=["date"])
    for c in ["status", "fulfilment", "category", "size", "ship_state", "ship_service_level"]:
        df[c] = df[c].astype("category")
    return df


df = load_data()

# ------------------------------------------------------------------ sidebar
st.sidebar.header("Filters")
min_d, max_d = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
categories = st.sidebar.multiselect("Category", sorted(df["category"].unique()))
states = st.sidebar.multiselect("Ship state", sorted(df["ship_state"].unique()))
fulfilment = st.sidebar.multiselect("Fulfilment", sorted(df["fulfilment"].unique()))
b2b = st.sidebar.radio("Customer type", ["All", "B2C", "B2B"], horizontal=True)

f = df
if isinstance(date_range, tuple) and len(date_range) == 2:
    f = f[(f["date"].dt.date >= date_range[0]) & (f["date"].dt.date <= date_range[1])]
if categories:
    f = f[f["category"].isin(categories)]
if states:
    f = f[f["ship_state"].isin(states)]
if fulfilment:
    f = f[f["fulfilment"].isin(fulfilment)]
if b2b != "All":
    f = f[f["b2b"] == (b2b == "B2B")]

st.title("🛒 E-Commerce Sales Analytics Dashboard")
st.caption("Amazon India sales report - orders from 31 Mar 2022 to 29 Jun 2022 "
           "(March contains a single day of data).")

if f.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ------------------------------------------------------------------ KPIs
sales = f[f["is_valid_sale"]]
total_orders = len(f)
revenue = sales["revenue"].sum()
units = sales["qty"].sum()
aov = revenue / max(len(sales), 1)
cancel_rate = f["is_cancelled"].mean() * 100
return_rate = f["is_returned"].mean() * 100

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Revenue (INR)", f"₹{revenue/1e6:,.2f}M")
c2.metric("Orders", f"{total_orders:,}")
c3.metric("Units sold", f"{int(units):,}")
c4.metric("Avg order value", f"₹{aov:,.0f}")
c5.metric("Cancel rate", f"{cancel_rate:.1f}%")
c6.metric("Return rate", f"{return_rate:.1f}%")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🏷️ Products", "🗺️ Geography", "🚚 Operations"])

# ------------------------------------------------------------------ trends
with tab1:
    daily = sales.groupby("date", as_index=False)["revenue"].sum()
    daily["7-day avg"] = daily["revenue"].rolling(7, min_periods=1).mean()
    fig = px.line(daily, x="date", y=["revenue", "7-day avg"], title="Daily revenue")
    fig.update_layout(legend_title_text="", yaxis_title="INR")
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    monthly = sales.groupby("month", as_index=False)["revenue"].sum()
    col_a.plotly_chart(px.bar(monthly, x="month", y="revenue", title="Monthly revenue"),
                       use_container_width=True)
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    wd = sales.groupby("weekday", as_index=False, observed=True)["revenue"].sum()
    wd["weekday"] = pd.Categorical(wd["weekday"], order, ordered=True)
    col_b.plotly_chart(px.bar(wd.sort_values("weekday"), x="weekday", y="revenue",
                              title="Revenue by weekday"), use_container_width=True)

# ------------------------------------------------------------------ products
with tab2:
    col_a, col_b = st.columns(2)
    cat = sales.groupby("category", as_index=False, observed=True)["revenue"].sum()
    col_a.plotly_chart(px.pie(cat, names="category", values="revenue", hole=0.45,
                              title="Revenue share by category"), use_container_width=True)
    size = sales.groupby("size", as_index=False, observed=True)["qty"].sum()
    col_b.plotly_chart(px.bar(size.sort_values("qty", ascending=False), x="size", y="qty",
                              title="Units sold by size"), use_container_width=True)

    top = (sales.groupby("style", as_index=False)
                .agg(revenue=("revenue", "sum"), units=("qty", "sum"))
                .nlargest(15, "revenue"))
    st.plotly_chart(px.bar(top.sort_values("revenue"), x="revenue", y="style", orientation="h",
                           title="Top 15 styles by revenue"), use_container_width=True)

# ------------------------------------------------------------------ geography
with tab3:
    col_a, col_b = st.columns(2)
    st_rev = (sales.groupby("ship_state", as_index=False, observed=True)["revenue"].sum()
                   .nlargest(15, "revenue"))
    col_a.plotly_chart(px.bar(st_rev.sort_values("revenue"), x="revenue", y="ship_state",
                              orientation="h", title="Top 15 states by revenue"),
                       use_container_width=True)
    city_rev = sales.groupby("ship_city", as_index=False)["revenue"].sum().nlargest(15, "revenue")
    col_b.plotly_chart(px.bar(city_rev.sort_values("revenue"), x="revenue", y="ship_city",
                              orientation="h", title="Top 15 cities by revenue"),
                       use_container_width=True)

# ------------------------------------------------------------------ operations
with tab4:
    col_a, col_b = st.columns(2)
    status = f["status"].value_counts().reset_index()
    status.columns = ["status", "orders"]
    col_a.plotly_chart(px.bar(status.sort_values("orders"), x="orders", y="status",
                              orientation="h", title="Orders by status"),
                       use_container_width=True)
    ful = (f.groupby("fulfilment", observed=True)
            .agg(orders=("order_id", "count"), cancelled=("is_cancelled", "mean"),
                 returned=("is_returned", "mean")).reset_index())
    ful[["cancelled", "returned"]] *= 100
    col_b.plotly_chart(px.bar(ful, x="fulfilment", y=["cancelled", "returned"], barmode="group",
                              title="Cancel / return rate (%) by fulfilment"),
                       use_container_width=True)

    sv = (f.groupby("ship_service_level", observed=True)
            .agg(orders=("order_id", "count"), cancelled=("is_cancelled", "mean")).reset_index())
    sv["cancelled"] *= 100
    st.dataframe(sv.rename(columns={"cancelled": "cancel rate %"}).round(2), hide_index=True)

with st.expander("View / download filtered data"):
    st.dataframe(f.head(1000))
    st.download_button("Download filtered CSV", f.to_csv(index=False).encode(),
                       "filtered_sales.csv", "text/csv")
