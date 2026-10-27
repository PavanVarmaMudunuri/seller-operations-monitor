from datetime import timedelta
import pandas as pd
import numpy as np

def calculate_payouts(data, cfg):
    sellers=data["seller"].set_index("seller_id").to_dict("index")
    listing_cat=dict(zip(data["product_listing"].listing_id, data["product_listing"].category))
    lines=data["order_line"]
    fulfill_dict=data["fulfillment"].set_index("order_line_id").to_dict("index")
    disputes=data["dispute"]
    rules=data["commission_rule"]
    hold=int(cfg["business"]["payout_hold_days"])

    # Pre-index commission rates: (category, tier) -> rate
    rate_map={(r.category, r.commission_tier): float(r.commission_rate) for r in rules.itertuples()}

    # Pre-index disputes
    open_disputes=set(disputes[(disputes.status=="OPEN") & (disputes.financially_applicable)].order_line_id)
    resolved_dispute_amounts=disputes[disputes.financially_applicable].groupby("order_line_id").dispute_amount.sum().to_dict()

    payout_lines=[]
    payout_rows=[]
    payout_counter=0

    # One payout batch per seller for all currently payable lines.
    for seller_id, grp in lines.groupby("seller_id"):
        seller=sellers.get(seller_id)
        if not seller or seller["status"]!="ACTIVE":
            continue
        reserve_rate=float(seller["reserve_rate"])
        tier=seller["commission_tier"]

        line_acc=[]
        for ol in grp.itertuples():
            f=fulfill_dict.get(ol.order_line_id)
            if not f or f["fulfillment_status"]!="DELIVERED" or pd.isna(f["actual_delivery_date"]):
                continue
            if f["return_status"]=="RETURNED":
                continue
            if ol.order_line_id in open_disputes:
                continue

            delivery=pd.Timestamp(f["actual_delivery_date"]).date()
            payout_date=delivery+timedelta(days=hold)
            cat=listing_cat.get(ol.listing_id, "Electronics")
            rate=rate_map.get((cat, tier), 0.10)
            gross=float(ol.line_total)
            commission=round(gross*rate,2)
            dispute_deduction=round(float(resolved_dispute_amounts.get(ol.order_line_id, 0.0)),2)
            reserve=round(max(0,gross-commission-dispute_deduction)*reserve_rate,2)
            net=round(gross-commission-dispute_deduction-reserve,2)
            line_acc.append((ol,payout_date,gross,commission,dispute_deduction,reserve,net))

        if not line_acc:
            continue
        payout_counter+=1
        pid=f"PAYOUT-2026-{payout_counter:06d}"
        total=round(sum(x[-1] for x in line_acc),2)
        payout_date=max(x[1] for x in line_acc)
        payout_rows.append([pid,seller_id,payout_date.isoformat(),total,"ELIGIBLE",None])
        for pos,(ol,pdate,gross,commission,dispute_deduction,reserve,net) in enumerate(line_acc,1):
            payout_lines.append([f"PL-{pid}-{pos:04d}",pid,ol.order_line_id,gross,commission,0.0,
                                 dispute_deduction,reserve,net])
    payouts=pd.DataFrame(payout_rows,columns=[
        "payout_id","seller_id","payout_date","total_amount","eligibility_status","exception_code"])
    payout_lines_df=pd.DataFrame(payout_lines,columns=[
        "payout_line_id","payout_id","order_line_id","gross_amount","commission_amount",
        "refund_amount","dispute_deduction","reserve_amount","net_payout_amount"])
    return payouts,payout_lines_df
