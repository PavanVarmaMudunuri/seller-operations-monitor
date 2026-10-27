import random
from datetime import date, timedelta
import numpy as np
import pandas as pd

CATEGORIES = ["Electronics","Fashion","Home","Beauty","Grocery","Sports"]
REGIONS = ["Telangana","Andhra Pradesh","Karnataka","Tamil Nadu","Maharashtra","Delhi"]
CARRIERS = ["Delhivery","BlueDart","EcomExpress","DTDC","XpressBees"]

def date_str(d): return d.isoformat()

def money(x): return round(float(x), 2)

def generate_all(cfg):
    seed = int(cfg["seed"])
    rng = np.random.default_rng(seed)
    random.seed(seed)
    v = cfg["volume"]
    b = cfg["business"]
    base_date = date(2026, 10, 1)

    # Sellers
    sellers = []
    for i in range(1, v["sellers"]+1):
        sid = f"SELL-{i:06d}"
        join = base_date - timedelta(days=int(rng.integers(30, 900)))
        risk = rng.random()
        status = "SUSPENDED" if risk < 0.03 else ("PENDING" if risk < 0.05 else "ACTIVE")
        tier = "PREMIUM" if rng.random() < 0.15 else "STANDARD"
        reserve = b["reserve_rate_high_risk"] if risk < 0.10 else (
            b["reserve_rate_new"] if (base_date-join).days < 90 else b["reserve_rate_established"])
        sellers.append([sid,f"Seller {i:06d}",status,date_str(join),
                        random.choice(CATEGORIES),tier,reserve])
    sellers_df = pd.DataFrame(sellers, columns=[
        "seller_id","seller_name","status","join_date","category","commission_tier","reserve_rate"
    ])

    active_sellers = sellers_df[sellers_df.status=="ACTIVE"].seller_id.tolist() or sellers_df.seller_id.tolist()

    # Listings
    listings = []
    for i in range(1, v["listings"]+1):
        sid = active_sellers[(i-1) % len(active_sellers)]
        lno = i
        lid = f"LIST-{sid}-{lno:06d}"
        category = sellers_df.loc[sellers_df.seller_id==sid, "category"].iloc[0]
        price = money(np.exp(rng.normal(np.log(900), 0.85)))
        listings.append([lid,sid,f"PROD-{i:08d}",f"SKU-{i:08d}",
                         f"{category} Product {i:06d}",category,price,
                         int(rng.integers(0,250)),"ACTIVE",date_str(base_date-timedelta(days=int(rng.integers(0,180))))])
    listings_df = pd.DataFrame(listings, columns=[
        "listing_id","seller_id","product_id","sku","title","category","price",
        "stock_quantity","listing_status","created_at"
    ])

    # Customers
    customers=[]
    for i in range(1,v["customers"]+1):
        customers.append([f"CUST-{i:07d}",random.choice(REGIONS),
                          date_str(base_date-timedelta(days=int(rng.integers(30,1000))))])
    customers_df=pd.DataFrame(customers,columns=["customer_id","region","created_at"])

    # Orders and lines
    orders=[]
    lines=[]
    order_line_counter=0
    listing_records = listings_df.to_dict("records")
    for i in range(1,v["orders"]+1):
        oid=f"ORD-2026-{i:06d}"
        od=base_date-timedelta(days=int(rng.integers(0,90)))
        customer_id=f"CUST-{int(rng.integers(1,v['customers']+1)):07d}"
        n_lines=int(rng.choice([1,1,1,2,2,3,4], p=[.25,.2,.15,.18,.12,.07,.03]))
        selected=rng.choice(len(listing_records), size=n_lines, replace=False)
        gross=0
        for pos, idx in enumerate(selected, start=1):
            r=listing_records[int(idx)]
            qty=int(rng.integers(1,4))
            discount=money(r["price"]*rng.uniform(0,.12))
            total=money(qty*r["price"]-discount)
            order_line_counter += 1
            olid=f"OL-{oid}-{pos:02d}"
            lines.append([olid,oid,r["listing_id"],r["seller_id"],qty,r["price"],discount,total])
            gross += total
        shipping=money(rng.uniform(0,150))
        discount_total=money(gross*0.02*rng.random())
        tax=money(max(0,gross-discount_total)*rng.uniform(.03,.18))
        net=money(gross-discount_total+shipping+tax)
        status="DELIVERED" if rng.random()<.82 else random.choice(["SHIPPED","PROCESSING","CANCELLED","RETURNED"])
        orders.append([oid,customer_id,date_str(od),"INR",status,money(gross),discount_total,shipping,tax,net])
    orders_df=pd.DataFrame(orders,columns=[
        "order_id","customer_id","order_date","currency","order_status","gross_amount",
        "discount_amount","shipping_amount","tax_amount","net_order_amount"
    ])
    lines_df=pd.DataFrame(lines,columns=[
        "order_line_id","order_id","listing_id","seller_id","quantity","unit_price",
        "discount_amount","line_total"
    ])

    # Fulfillments derived from lines
    fulfill=[]
    for _,r in lines_df.iterrows():
        od=pd.Timestamp(orders_df.loc[orders_df.order_id==r.order_id,"order_date"].iloc[0]).date()
        promised_ship=od+timedelta(days=int(rng.integers(1,4)))
        actual_ship=promised_ship+timedelta(days=int(rng.choice([0,0,0,1,2,3],p=[.50,.15,.1,.1,.1,.05])))
        promised_delivery=actual_ship+timedelta(days=int(rng.integers(2,6)))
        delivered=rng.random()<.86
        actual_delivery=promised_delivery+timedelta(days=int(rng.choice([0,0,1,2,4],p=[.55,.15,.15,.1,.05]))) if delivered else None
        status="DELIVERED" if delivered else random.choice(["SHIPPED","PROCESSING","CANCELLED"])
        ret="RETURNED" if delivered and rng.random()<.06 else "NONE"
        delay=(actual_ship-promised_ship).days
        sla="ON_TIME" if delay<=0 else ("LATE" if delay<=2 else "SEVERELY_LATE")
        fid=f"FUL-{r.order_line_id}"
        fulfill.append([fid,r.order_line_id,r.seller_id,status,date_str(promised_ship),
                        date_str(actual_ship),date_str(promised_delivery),
                        date_str(actual_delivery) if actual_delivery else None,
                        random.choice(CARRIERS),f"TRK-{rng.integers(10**10,10**11-1)}",ret,sla])
    fulfill_df=pd.DataFrame(fulfill,columns=[
        "fulfillment_id","order_line_id","seller_id","fulfillment_status",
        "promised_ship_date","actual_ship_date","promised_delivery_date",
        "actual_delivery_date","carrier","tracking_number","return_status","sla_status"
    ])

    # Reviews only for delivered lines, with seller rating influenced by SLA
    reviews=[]
    delivered_lines=fulfill_df[fulfill_df.fulfillment_status=="DELIVERED"]
    for i,(_,f) in enumerate(delivered_lines.sample(frac=.55,random_state=seed).iterrows(),start=1):
        oid=lines_df.loc[lines_df.order_line_id==f.order_line_id,"order_id"].iloc[0]
        rating=int(np.clip(round(rng.normal(4.1 if f.sla_status=="ON_TIME" else 3.3,.7)),1,5))
        reviews.append([f"REV-{i:08d}",oid,f.seller_id,rating,date_str(base_date)])
    reviews_df=pd.DataFrame(reviews,columns=["review_id","order_id","seller_id","rating","review_date"])

    # Commission rules
    rules=[]
    rule_no=0
    for cat,rate in b["commission_by_category"].items():
        for tier in ["STANDARD","PREMIUM"]:
            rule_no+=1
            final_rate=b["commission_premium"] if tier=="PREMIUM" else rate
            rules.append([f"CR-{rule_no:04d}",cat,tier,final_rate,"2026-01-01",None])
    rules_df=pd.DataFrame(rules,columns=[
        "commission_rule_id","category","commission_tier","commission_rate","effective_from","effective_to"
    ])

    # Disputes: select order lines, deterministic volume
    dispute_rows=[]
    candidates=lines_df.sample(n=min(v["disputes"],len(lines_df)),random_state=seed)
    for i,(_,ol) in enumerate(candidates.iterrows(),start=1):
        opened=base_date-timedelta(days=int(rng.integers(0,60)))
        resolved = opened+timedelta(days=int(rng.integers(2,20))) if rng.random()<.7 else None
        status="RESOLVED" if resolved else "OPEN"
        amount=money(ol.line_total*rng.uniform(.2,1))
        dtype=random.choice(["CHARGEBACK","ITEM_NOT_RECEIVED","DAMAGED","WRONG_ITEM"])
        applicable=True
        dispute_rows.append([f"DSP-2026-{i:06d}",ol.order_id,ol.order_line_id,ol.seller_id,dtype,
                             status,amount,date_str(opened),date_str(resolved) if resolved else None,applicable])
    disputes_df=pd.DataFrame(dispute_rows,columns=[
        "dispute_id","order_id","order_line_id","seller_id","dispute_type","status",
        "dispute_amount","opened_date","resolved_date","financially_applicable"
    ])

    # Status history
    events=[]
    for i,(_,s) in enumerate(sellers_df[sellers_df.status=="SUSPENDED"].iterrows(),start=1):
        events.append([f"SE-{i:06d}",s.seller_id,"ACTIVE","SUSPENDED",
                       f"{base_date}T09:00:00","Synthetic risk/service suspension"])
    status_events_df=pd.DataFrame(events,columns=[
        "event_id","seller_id","old_status","new_status","effective_at","reason"
    ])

    return {
        "seller":sellers_df,"product_listing":listings_df,"customer":customers_df,
        "orders":orders_df,"order_line":lines_df,"fulfillment":fulfill_df,
        "customer_review":reviews_df,"dispute":disputes_df,
        "commission_rule":rules_df,"seller_status_event":status_events_df
    }
