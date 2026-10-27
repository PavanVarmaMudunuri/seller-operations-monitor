import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
EXPORTS = ROOT / "data" / "exports"
GT_PATH = ROOT / "ground_truth" / "ground_truth.csv"

st.set_page_config(page_title="Seller Operations Monitor", layout="wide", page_icon="📊")

# Sidebar Controls
st.sidebar.title("Operations Control")
if st.sidebar.button("🔄 Force Reload Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if not (REPORTS / "seller_metrics.csv").exists():
    st.warning("Reports not found. Run the pipeline first: python scripts/run_pipeline.py --config configs/full.yaml")
    st.stop()

# Load fresh data
seller = pd.read_csv(REPORTS / "seller_metrics.csv")
payout = pd.read_csv(REPORTS / "payout_metrics.csv")
exceptions = pd.read_csv(REPORTS / "exception_metrics.csv")
gt = pd.read_csv(GT_PATH)

mode = "Full Production Scale (2,000 Sellers)" if len(seller) > 100 else "Starter Scale (20 Sellers)"
st.sidebar.success(f"**Loaded Mode:**\n{mode}")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.title("Seller Operations Monitor")
st.caption(f"Operational health, fulfillment SLAs, financial reconciliation, and exception tracking — **{mode}**")

# Top KPI Metric Cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("Sellers", f"{len(seller):,}")
c2.metric("Orders", f"{int(seller.orders.sum()):,}")
c3.metric("GMV", f"₹{seller.gmv.sum():,.0f}")
c4.metric("Ground-truth exceptions", f"{len(gt):,}")

st.markdown("---")

# Section 1: Seller Service Levels
st.subheader("Seller Service Levels")
st.caption("Displaying lowest scoring merchants requiring operational intervention (sorted by service score).")
display_sellers = seller.sort_values("service_score").head(25).copy()
st.dataframe(display_sellers, use_container_width=True)

st.markdown("---")

# Section 2: Payout Reconciliation
st.subheader("Payout Settlement & Reconciliation")
st.caption("Disbursement batches sorted by reconciliation discrepancy (gross vs. net payout deductions).")
if len(payout):
    payout["reconciliation_difference"] = payout["reconciliation_difference"].round(2)
    display_payouts = payout.sort_values(
        "reconciliation_difference",
        key=lambda x: x.abs(),
        ascending=False
    ).head(25)
    st.dataframe(display_payouts, use_container_width=True)

st.markdown("---")

# Section 3: Injected Exceptions & Ground Truth
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Exception Classes")
    st.caption("Summary count and severity of injected operational exceptions.")
    st.dataframe(exceptions, use_container_width=True)
    
    st.subheader("Exception Distribution")
    st.bar_chart(gt["issue_type"].value_counts())

with col_right:
    st.subheader("Service Score Distribution")
    st.caption("Distribution of merchants across performance health bands.")
    st.bar_chart(seller["service_band"].value_counts())
