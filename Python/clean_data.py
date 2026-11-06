"""
Step 1 - Data cleaning.
Reads the raw Amazon Sale Report and writes a small, analysis-ready file
(Dataset/cleaned_sales.csv.gz) that the dashboard loads on Render.

Run from the project root:  python Python/clean_data.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "Dataset" / "Amazon Sale Report.csv"
OUT = ROOT / "Dataset" / "cleaned_sales.csv.gz"

# Several spellings of the same state exist in the raw file.
STATE_FIX = {
    "NEW DELHI": "DELHI", "ORISSA": "ODISHA", "PONDICHERRY": "PUDUCHERRY",
    "RAJSHTHAN": "RAJASTHAN", "RAJSTHAN": "RAJASTHAN", "RJ": "RAJASTHAN",
    "PB": "PUNJAB", "PUNJAB/MOHALI/ZIRAKPUR": "PUNJAB", "NL": "NAGALAND",
    "AR": "ARUNACHAL PRADESH", "ANDAMAN & NICOBAR": "ANDAMAN & NICOBAR ISLANDS",
}

# Status groups used by the KPIs
CANCELLED = {"Cancelled"}
RETURNED = {"Shipped - Returned to Seller", "Shipped - Returning to Seller",
            "Shipped - Rejected by Buyer"}


def clean(raw_path: Path = RAW) -> pd.DataFrame:
    df = pd.read_csv(raw_path, low_memory=False)

    # 1. drop useless columns
    df = df.drop(columns=["index", "Unnamed: 22", "ship-country", "currency"], errors="ignore")
    df.columns = (df.columns.str.strip().str.lower()
                  .str.replace(r"[\s\-]+", "_", regex=True))

    # 2. remove exact duplicates
    df = df.drop_duplicates()

    # 3. dates (file stores MM-DD-YY)
    df["date"] = pd.to_datetime(df["date"], format="%m-%d-%y")
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["weekday"] = df["date"].dt.day_name()

    # 4. text standardisation
    df["category"] = df["category"].str.strip().str.title()
    df["ship_state"] = df["ship_state"].str.strip().str.upper().replace(STATE_FIX)
    df["ship_city"] = df["ship_city"].str.strip().str.title()

    # 5. missing values
    df["amount"] = df["amount"].fillna(0.0)
    df["ship_state"] = df["ship_state"].fillna("UNKNOWN")
    df["ship_city"] = df["ship_city"].fillna("Unknown")
    df["has_promotion"] = df["promotion_ids"].notna()
    df["fulfilment"] = df["fulfilment"].str.strip()
    df = df.drop(columns=["promotion_ids", "fulfilled_by", "courier_status", "ship_postal_code"])

    # 6. business flags
    df["is_cancelled"] = df["status"].isin(CANCELLED)
    df["is_returned"] = df["status"].isin(RETURNED)
    df["is_valid_sale"] = ~df["is_cancelled"] & (df["amount"] > 0)
    df["revenue"] = df["amount"].where(df["is_valid_sale"], 0.0)

    # 7. memory friendly dtypes
    for c in ["status", "fulfilment", "sales_channel", "ship_service_level",
              "category", "size", "ship_state", "weekday", "month"]:
        df[c] = df[c].astype("category")
    return df.reset_index(drop=True)


if __name__ == "__main__":
    out = clean()
    out.to_csv(OUT, index=False, compression="gzip")
    print(f"Saved {len(out):,} rows -> {OUT}  ({OUT.stat().st_size/1e6:.1f} MB)")
    print(out.dtypes)
