# 🛒 E-Commerce Sales Analytics Dashboard

End-to-end analytics project on an Amazon India sales dataset (~129k order lines, 31 Mar - 29 Jun 2022):
data cleaning with Python/Pandas, exploratory analysis, an interactive Streamlit dashboard deployed on Render,
and a Power BI version.

**Live demo:** `https://<your-service>.onrender.com`  _(add after deploying)_

![Dashboard](Images/Dashboard1.png)

## Features
- Cleaning pipeline: duplicates removed, dates parsed, 69 messy state spellings merged into 38 states, business flags added
- KPIs: revenue, orders, units, average order value, cancellation rate, return rate
- Interactive filters: date, category, state, fulfilment, B2B/B2C
- Tabs: Trends, Products, Geography, Operations + CSV download of filtered data

## Project structure
```
E-Commerce-Sales-Analytics-Dashboard/
├── Dataset/            raw CSV + cleaned_sales.csv.gz (used by the app)
├── PowerBI/            Power BI guide (+ your .pbix)
├── Images/             dashboard screenshots
├── Python/             clean_data.py, analysis.ipynb, generate_report.py
├── app.py              Streamlit dashboard (Render entry point)
├── render.yaml         Render blueprint
├── requirements.txt
├── README.md
├── ROADMAP.md
└── Report.pdf
```

## Run locally
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python Python/clean_data.py        # regenerates Dataset/cleaned_sales.csv.gz
streamlit run app.py
```
For the notebook and PDF report: `pip install -r requirements-dev.txt`, then `jupyter notebook Python/analysis.ipynb`
and `python Python/generate_report.py`.

## Deploy on Render
1. Push this folder to GitHub (see ROADMAP.md).
2. Render > New > **Web Service** > connect the repo.
3. Runtime `Python 3`, Build `pip install -r requirements.txt`,
   Start `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   (or choose **Blueprint** and let `render.yaml` fill this in).
4. Deploy. The free plan sleeps when idle, so the first load can take ~1 minute.

## Key insights
- "Set" and "Kurta" together account for about 77% of revenue.
- Maharashtra is the top state; the top 5 states make up about 56% of revenue.
- Overall cancellation rate is about 14%; Merchant-fulfilled orders cancel more than Amazon-fulfilled.
- March has only one day of data; compare April-June only.

## Tech stack
Python, Pandas, Plotly, Streamlit, Matplotlib/Seaborn, Power BI, Git/GitHub, Render
