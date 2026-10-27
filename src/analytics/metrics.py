import pandas as pd
import numpy as np

def calculate_metrics(data,payouts,payout_lines,ground_truth):
    s=data["seller"]
    ol=data["order_line"]
    f=data["fulfillment"]
    d=data["dispute"]
    r=data["customer_review"]

    base=s.set_index("seller_id")[["seller_name","status"]].copy()
    orders=ol.groupby("seller_id").order_id.nunique().rename("orders")
    gmv=ol.groupby("seller_id").line_total.sum().rename("gmv")
    sla=f.groupby("seller_id").sla_status.apply(lambda x:(x=="ON_TIME").mean()).rename("on_time_rate")
    returned=f.groupby("seller_id").return_status.apply(lambda x:(x=="RETURNED").mean()).rename("return_rate")
    dispute_rate=d.groupby("seller_id").dispute_id.nunique().rename("disputes")
    ratings=r.groupby("seller_id").rating.mean().rename("avg_rating")

    m=base.join([orders,gmv,sla,returned,dispute_rate,ratings]).fillna(0)
    delivered_rate=f.groupby("seller_id").fulfillment_status.apply(lambda x:(x=="DELIVERED").mean()).rename("delivery_success_rate")
    m=m.join(delivered_rate).fillna(0)
    dispute_free=(1-(m.disputes/(m.orders.replace(0,np.nan)))).clip(lower=0,upper=1).fillna(1)
    m["dispute_free_rate"]=dispute_free
    m["rating_score"]=m.avg_rating/5
    m["service_score"]=(.40*m.on_time_rate+.25*m.delivery_success_rate+
                         .20*m.dispute_free_rate+.15*m.rating_score)*100
    m["service_band"]=pd.cut(m.service_score,[-1,70,80,90,101],
                              labels=["AT_RISK","WATCH","GOOD","EXCELLENT"],right=False)

    payout_summary=payout_lines.groupby("payout_id").agg(
        gross=("gross_amount","sum"),commission=("commission_amount","sum"),
        dispute_deduction=("dispute_deduction","sum"),reserve=("reserve_amount","sum"),
        net=("net_payout_amount","sum")).reset_index()
    payout_summary=payout_summary.merge(payouts[["payout_id","seller_id","total_amount","eligibility_status"]],
                                         on="payout_id",how="left")
    payout_summary["reconciliation_difference"]=payout_summary.total_amount-payout_summary.net

    exception_summary=ground_truth.groupby(["issue_type","severity"]).size().reset_index(name="count")
    return m.reset_index(),payout_summary,exception_summary
