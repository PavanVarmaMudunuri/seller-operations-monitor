import pandas as pd

def inject_anomalies(data, payouts, payout_lines, cfg):
    gt=[]
    counters={k:0 for k in cfg["anomalies"]}
    # Work on copies.
    sellers=data["seller"].copy()
    listings=data["product_listing"].copy()
    disputes=data["dispute"].copy()
    payouts=payouts.copy()
    payout_lines=payout_lines.copy()

    # 1: payout before hold release: move payout date backwards.
    n=cfg["anomalies"]["payout_before_hold"]
    for i in range(min(n,len(payouts))):
        row=payouts.iloc[i]
        pid=row.payout_id
        pl=payout_lines[payout_lines.payout_id==pid]
        if len(pl)==0: continue
        payouts.loc[payouts.payout_id==pid,"payout_date"]="2026-01-01"
        gt.append([f"GT-{len(gt)+1:06d}",pid,"PAYOUT_BEFORE_HOLD_RELEASE","BLOCK","HIGH"])

    # 2: duplicate commission: add a duplicate payout line for selected payouts.
    n=cfg["anomalies"]["duplicate_commission"]
    for i in range(min(n,max(0,len(payouts)-1))):
        pid=payouts.iloc[n+i if n+i<len(payouts) else i].payout_id
        pl=payout_lines[payout_lines.payout_id==pid]
        if len(pl)==0: continue
        base=pl.iloc[0].copy()
        base["payout_line_id"]=f"{base.payout_line_id}-DUP"
        base["commission_amount"]=float(base.commission_amount)
        payout_lines=pd.concat([payout_lines,pd.DataFrame([base])],ignore_index=True)
        gt.append([f"GT-{len(gt)+1:06d}",pid,"COMMISSION_APPLIED_TWICE","REVIEW","HIGH"])

    # 3: suspended seller continues listing: suspend sellers and leave active listings.
    n=cfg["anomalies"]["suspended_listing"]
    active_sids=[sid for sid in sellers[sellers.status=="ACTIVE"].seller_id
                 if len(listings[(listings.seller_id==sid)&(listings.listing_status=="ACTIVE")])>0]
    for i,sid in enumerate(active_sids[:n]):
        sellers.loc[sellers.seller_id==sid,"status"]="SUSPENDED"
        active_listing=listings[(listings.seller_id==sid)&(listings.listing_status=="ACTIVE")]
        lid=active_listing.iloc[0].listing_id
        gt.append([f"GT-{len(gt)+1:06d}",lid,"SUSPENDED_SELLER_CONTINUES_LISTING","BLOCK","HIGH"])

    # 4: dispute not deducted: zero out one applicable dispute deduction.
    n=cfg["anomalies"]["dispute_not_deducted"]
    applicable=disputes[(disputes.status=="RESOLVED")&(disputes.financially_applicable)&(disputes.order_line_id.isin(payout_lines.order_line_id))]
    for i,(_,d) in enumerate(applicable.head(n).iterrows()):
        pl=payout_lines[payout_lines.order_line_id==d.order_line_id]
        if len(pl)==0: continue
        payout_lines.loc[payout_lines.order_line_id==d.order_line_id,"dispute_deduction"]=0.0
        gt.append([f"GT-{len(gt)+1:06d}",d.order_line_id,"DISPUTE_NOT_DEDUCTED","HOLD","HIGH"])

    # 5: payout total mismatch.
    n=cfg["anomalies"]["payout_mismatch"]
    for i in range(min(n,len(payouts))):
        pid=payouts.iloc[-(i+1)].payout_id
        payouts.loc[payouts.payout_id==pid,"total_amount"] = round(
            float(payouts.loc[payouts.payout_id==pid,"total_amount"].iloc[0])+100,2)
        gt.append([f"GT-{len(gt)+1:06d}",pid,"PAYOUT_TOTAL_MISMATCH","BLOCK","CRITICAL"])

    ground=pd.DataFrame(gt,columns=["case_id","entity_id","issue_type","expected_decision","severity"])
    return data | {"seller":sellers,"product_listing":listings,"dispute":disputes}, payouts, payout_lines, ground
