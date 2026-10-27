from datetime import timedelta
import pandas as pd
import numpy as np

def calculate_payouts(data, cfg):
    sellers=data["seller"].set_index("seller_id")
    listings=data["product_listing"].set_index("listing_id")
    lines=data["order_line"]
    fulfill=data["fulfillment"].set_index("order_line_id")
    disputes=data["dispute"]
    rules=data["commission_rule"]
    hold=int(cfg["business"]["payout_hold_days"])

    payout_lines=[]
    payout_rows=[]
    payout_counter=0

    # One payout batch per seller for all currently payable lines.
    for seller_id, grp in lines.groupby("seller_id"):
        seller=sellers.loc[seller_id]
        line_acc=[]
        for _,ol in grp.iterrows():
            f=fulfill.loc[ol.order_line_id]
            if f.fulfillment_status!="DELIVERED" or pd.isna(f.actual_delivery_date):
                continue
            delivery=pd.Timestamp(f.actual_delivery_date).date()
            payout_date=delivery+timedelta(days=hold)
            if seller.status!="ACTIVE":
                continue
            if f.return_status=="RETURNED":
                continue
            open_dispute=disputes[(disputes.order_line_id==ol.order_line_id) &
                                  (disputes.status=="OPEN") &
                                  (disputes.financially_applicable)]
            if len(open_dispute)>0:
                continue

            listing=listings.loc[ol.listing_id]
            rate=float(rules[(rules.category==listing.category) &
                             (rules.commission_tier==seller.commission_tier)].iloc[0].commission_rate)
            gross=float(ol.line_total)
            commission=round(gross*rate,2)
            resolved_dispute=disputes[(disputes.order_line_id==ol.order_line_id) &
                                      (disputes.financially_applicable)]
            dispute_deduction=round(float(resolved_dispute.dispute_amount.sum()),2)
            reserve=round(max(0,gross-commission-dispute_deduction)*float(seller.reserve_rate),2)
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
