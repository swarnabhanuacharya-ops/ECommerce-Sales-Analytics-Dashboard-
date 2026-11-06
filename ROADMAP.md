# Roadmap: E-Commerce Sales Analytics Dashboard

| Phase | Goal | Output | Time |
|------|------|--------|------|
| 1 Setup | Create repo + folders, install Python, VS Code, Git | Project skeleton | 0.5 day |
| 2 Understand data | Read columns, check nulls/duplicates, define metrics | Data notes | 0.5 day |
| 3 Clean | Run `Python/clean_data.py` | `Dataset/cleaned_sales.csv.gz` | 0.5 day |
| 4 Explore (EDA) | Fill in `Python/analysis.ipynb`, write 5-8 insights | Notebook with outputs | 1-2 days |
| 5 Power BI | Follow `PowerBI/POWERBI_GUIDE.md`, 3 pages | `.pbix` + 3 screenshots in `Images/` | 2 days |
| 6 Web dashboard | Run/customise `app.py` locally | Working Streamlit app | 1-2 days |
| 7 Report | `python Python/generate_report.py`, add your own insights | `Report.pdf` | 0.5 day |
| 8 Docs | Update README (screenshots, insights, live link) | Polished README | 0.5 day |
| 9 GitHub | Push the repo | Public repo | 0.5 hour |
| 10 Deploy | Render web service | Live URL | 0.5 hour |
| 11 Resume | Add bullets + link | Resume / LinkedIn | 0.5 hour |

## Push to GitHub
```bash
cd E-Commerce-Sales-Analytics-Dashboard
git init
git add .
git commit -m "Initial commit: E-commerce sales analytics dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/E-Commerce-Sales-Analytics-Dashboard.git
git push -u origin main
```
Create the empty repo on github.com first (no README/licence). The raw CSV is ~69 MB: GitHub warns above
50 MB and rejects files above 100 MB, so this works, but if you prefer a lighter repo add
`Dataset/Amazon Sale Report.csv` to `.gitignore`; the app only needs `cleaned_sales.csv.gz` (4 MB).

## Deploy on Render
1. render.com > sign in with GitHub > **New + > Web Service** > pick the repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Instance type: Free > **Create Web Service**. Copy the URL into README.
5. Every `git push` to `main` redeploys automatically.

## Troubleshooting
- Build fails on Python version: set env var `PYTHON_VERSION=3.11.9`.
- App is slow on first open: free instances sleep; wait ~1 minute.
- Out of memory: keep using `cleaned_sales.csv.gz`, never the raw CSV, in `app.py`.

## Stretch goals (to stand out)
- SQL: load the CSV into SQLite/PostgreSQL and add `SQL/queries.sql` (top products, monthly growth, cancel rate by state).
- RFM-style segmentation or a simple revenue forecast (Prophet / statsmodels), with the caveat of only 3 months of data.
- Scheduled data refresh and unit tests for `clean_data.py`.

## Resume bullets
- Built an end-to-end sales analytics dashboard on 129K+ Amazon order records using Python, Pandas and Power BI.
- Cleaned and standardised raw data (duplicates, 69 inconsistent state names, missing values) and engineered KPIs: revenue, AOV, cancel and return rates.
- Deployed an interactive Streamlit app on Render with date, category, state and fulfilment filters.
