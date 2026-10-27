CREATE OR REPLACE VIEW vw_seller_performance AS
SELECT
    s.seller_id,
    s.seller_name,
    s.status,
    COUNT(DISTINCT ol.order_id) AS orders,
    COALESCE(SUM(ol.line_total),0) AS gmv,
    AVG(CASE WHEN f.sla_status='ON_TIME' THEN 1.0 ELSE 0.0 END) AS on_time_rate,
    AVG(CASE WHEN f.return_status='RETURNED' THEN 1.0 ELSE 0.0 END) AS return_rate,
    COALESCE(AVG(cr.rating),0) AS avg_rating
FROM seller s
LEFT JOIN order_line ol ON ol.seller_id=s.seller_id
LEFT JOIN fulfillment f ON f.order_line_id=ol.order_line_id
LEFT JOIN customer_review cr ON cr.order_id=ol.order_id AND cr.seller_id=s.seller_id
GROUP BY s.seller_id,s.seller_name,s.status;

CREATE OR REPLACE VIEW vw_payout_reconciliation AS
SELECT
    p.payout_id,
    p.seller_id,
    p.total_amount,
    COALESCE(SUM(pl.net_payout_amount),0) AS line_total,
    p.total_amount - COALESCE(SUM(pl.net_payout_amount),0) AS difference,
    p.eligibility_status
FROM payout p
LEFT JOIN payout_line pl ON pl.payout_id=p.payout_id
GROUP BY p.payout_id,p.seller_id,p.total_amount,p.eligibility_status;
