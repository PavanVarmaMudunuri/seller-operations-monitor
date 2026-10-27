import streamlit as st
import pandas as pd
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORTS=ROOT/"reports"
EXPORTS=ROOT/"data"/"exports"

st.set_page_config(page_title="Seller Operations Monitor",layout="wide")
st.title("Seller Operations Monitor")

if not (REPORTS/"seller_metrics.csv").exists():
    st.warning("Run the pipeline first: python scripts/run_pipeline.py --config configs/starter.yaml")
    st.stop()

seller=pd.read_csv(REPORTS/"seller_metrics.csv")
payout=pd.read_csv(REPORTS/"payout_metrics.csv")
exceptions=pd.read_csv(REPORTS/"exception_metrics.csv")
gt=pd.read_csv(ROOT/"ground_truth"/"ground_truth.csv")

c1,c2,c3,c4=st.columns(4)
c1.metric("Sellers",len(seller))
c2.metric("Orders",int(seller.orders.sum()))
c3.metric("GMV",f"₹{seller.gmv.sum():,.0f}")
c4.metric("Ground-truth exceptions",len(gt))

st.subheader("Seller service levels")
st.dataframe(seller.sort_values("service_score").head(25),use_container_width=True)

st.subheader("Payout reconciliation")
if len(payout):
    st.dataframe(payout.sort_values("reconciliation_difference",key=lambda x:x.abs(),ascending=False).head(25),
                 use_container_width=True)

st.subheader("Exception classes")
st.dataframe(exceptions,use_container_width=True)

st.subheader("Exception distribution")
st.bar_chart(gt["issue_type"].value_counts())

st.subheader("Service score distribution")
st.bar_chart(seller["service_band"].value_counts())
