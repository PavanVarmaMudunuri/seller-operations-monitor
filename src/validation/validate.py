import pandas as pd

def validate(data, payouts, payout_lines):
    results=[]
    def check(name, passed, detail=""):
        results.append({"check":name,"passed":bool(passed),"detail":detail})

    # PKs
    for name,df,key in [
        ("seller",data["seller"],"seller_id"),("product_listing",data["product_listing"],"listing_id"),
        ("customer",data["customer"],"customer_id"),("orders",data["orders"],"order_id"),
        ("order_line",data["order_line"],"order_line_id"),("fulfillment",data["fulfillment"],"fulfillment_id"),
        ("customer_review",data["customer_review"],"review_id"),("dispute",data["dispute"],"dispute_id"),
        ("commission_rule",data["commission_rule"],"commission_rule_id"),
        ("seller_status_event",data["seller_status_event"],"event_id"),
        ("payout",payouts,"payout_id"),("payout_line",payout_lines,"payout_line_id")
    ]:
        check(f"{name}.primary_key_unique",df[key].is_unique)

    # FKs
    checks=[
        ("listing->seller",set(data["product_listing"].seller_id)<=set(data["seller"].seller_id)),
        ("order->customer",set(data["orders"].customer_id)<=set(data["customer"].customer_id)),
        ("line->order",set(data["order_line"].order_id)<=set(data["orders"].order_id)),
        ("line->listing",set(data["order_line"].listing_id)<=set(data["product_listing"].listing_id)),
        ("line->seller",set(data["order_line"].seller_id)<=set(data["seller"].seller_id)),
        ("fulfillment->line",set(data["fulfillment"].order_line_id)<=set(data["order_line"].order_line_id)),
        ("dispute->line",set(data["dispute"].order_line_id)<=set(data["order_line"].order_line_id)),
        ("payout->seller",set(payouts.seller_id)<=set(data["seller"].seller_id)),
        ("payoutline->payout",set(payout_lines.payout_id)<=set(payouts.payout_id)),
        ("payoutline->line",set(payout_lines.order_line_id)<=set(data["order_line"].order_line_id)),
    ]
    for name,passed in checks: check(name,passed)

    check("listing.price_positive",(data["product_listing"].price>0).all())
    check("line.quantity_positive",(data["order_line"].quantity>0).all())
    check("review.rating_valid",data["customer_review"].rating.between(1,5).all() if len(data["customer_review"]) else True)
    check("commission.rate_valid",data["commission_rule"].commission_rate.between(0,1).all())
    check("line.arithmetic",(abs(
        data["order_line"].line_total -
        (data["order_line"].quantity*data["order_line"].unit_price-data["order_line"].discount_amount)
    )<0.011).all())

    # payout reconciliation is expected to have deliberate failures.
    reconciliation=payouts.merge(
        payout_lines.groupby("payout_id").net_payout_amount.sum().rename("line_total"),
        left_on="payout_id",right_index=True,how="left"
    )
    reconciliation["difference"]=reconciliation.total_amount-reconciliation.line_total.fillna(0)
    check("payout.reconciliation_clean", (reconciliation.difference.abs()<0.011).all(),
          f"{(reconciliation.difference.abs()>=0.011).sum()} deliberate/observed mismatches")

    report=pd.DataFrame(results)
    return report,reconciliation
