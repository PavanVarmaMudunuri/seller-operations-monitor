# Business Rules and Domain Logic

This document specifies the operational rules, lifecycle states, SLA criteria, and financial settlement logic implemented in the Seller Operations Monitor platform.

---

## 1. Seller Lifecycle and Status History

Marketplace sellers progress through defined operational states:

$$\text{PENDING} \longrightarrow \text{ACTIVE} \longleftrightarrow \text{SUSPENDED} \longrightarrow \text{REACTIVATED}$$

* **`PENDING`**: Onboarding state awaiting catalog verification and banking credentials.
* **`ACTIVE`**: Good standing; authorized to list products, receive orders, and disburse payouts.
* **`SUSPENDED`**: Restricted due to service score degradation (falling into the `AT_RISK` band), unresolved chargebacks, or high fraud risk. Suspended sellers cannot receive disbursements or list new items.
* **`REACTIVATED`**: Reinstated following dispute remediation or compliance review.

> **Traceability Guarantee**: Whenever a seller's status changes, an immutable event record is appended to `seller_status_event` containing the timestamp, old status, new status, and the operational reason. State changes never silently overwrite history.

---

## 2. Catalog Listing Lifecycle

$$\text{DRAFT} \longrightarrow \text{ACTIVE} \longleftrightarrow \text{PAUSED} \longrightarrow \text{DISCONTINUED}$$

* **Rule**: Only sellers in `ACTIVE` standing are permitted to publish active catalog listings.
* **Deliberate Exception**: The system injects cases where a seller was suspended yet active listings remained live (`SUSPENDED_SELLER_CONTINUES_LISTING`), testing whether downstream catalog monitors flag the breach.

---

## 3. Order Splitting & Fulfillment SLAs

When a customer places an order containing items from multiple distinct merchants, the order is split at the order-line level:
* Each `order_line` is tagged with the fulfilling merchant's `seller_id`.
* An independent `fulfillment` record tracks logistics dispatch, airway bill numbers, carrier assignment, and promised delivery windows.

### Shipment Service Level Agreements (SLAs)
Logistics performance is measured against promised carrier dispatch dates:
* **`ON_TIME`**: Dispatched on or before the promised ship date ($\Delta \le 0\text{ days}$).
* **`LATE`**: Dispatched 1 to 2 days after the promised ship date ($1 \le \Delta \le 2\text{ days}$).
* **`SEVERELY_LATE`**: Dispatched more than 2 days after the promised ship date ($\Delta > 2\text{ days}$).

---

## 4. Customer Returns and Dispute Management

* **Returns**: Eligible only post-delivery. Once marked as `RETURNED`, the order line is permanently disqualified from seller payout disbursement.
* **Disputes & Chargebacks**: Tracked under types `CHARGEBACK`, `ITEM_NOT_RECEIVED`, `DAMAGED`, or `WRONG_ITEM`.
* **Settlement Impact**:
  * Open disputes place a temporary freeze on the affected order line's payout line.
  * Resolved, financially applicable chargebacks are formally deducted from the seller's settlement batch.

---

## 5. Commission and Risk Reserve Structure

### Commission Schedule
Commissions are calculated dynamically per order line based on category and seller tier:
* **Premium Tier**: Discounted platform fee of 7.0% across all product lines.
* **Standard Tier**: Category-specific rates:
  * Electronics: 8.0%
  * Fashion: 12.0%
  * Home: 10.0%
  * Beauty: 11.0%
  * Grocery: 6.0%
  * Sports: 9.0%

### Rolling Risk Reserves
To protect the marketplace against post-settlement returns or chargebacks, a reserve hold is deducted from net proceeds:
* **Established Sellers** (> 90 days active, standard risk): **5.0%** reserve.
* **New Sellers** (< 90 days tenure): **15.0%** reserve.
* **High-Risk Sellers** (elevated dispute rate or risk profile): **25.0%** reserve.

---

## 6. Payout Settlement and Reconciliation

### Eligibility Checklist
An order line is approved for disbursement if and only if all five criteria are satisfied:
1. **Delivered**: Fulfillment status is confirmed `DELIVERED`.
2. **Hold Window Expired**: Current date $\ge \text{Actual Delivery Date} + 7\text{ days}$.
3. **Active Standing**: The fulfilling seller status is `ACTIVE`.
4. **Not Returned**: Return status is not `RETURNED`.
5. **No Open Disputes**: No unresolved, financially applicable disputes exist on the order line.

### Reconciliation Formula

$$\text{Net Payout} = \text{Gross Amount} - \text{Commission} - \text{Dispute Deductions} - \text{Reserve Amount}$$

$$\text{Batch Total Amount} = \sum_{i=1}^{N} \text{Net Payout Amount}_i$$

---

## 7. Seller Service Scoring Methodology

The overall health of a seller is quantified through a weighted service score between 0 and 100:

$$\text{Service Score} = \left( 0.40 \times \text{On-Time Rate} + 0.25 \times \text{Delivery Success Rate} + 0.20 \times \text{Dispute-Free Rate} + 0.15 \times \frac{\text{Average Rating}}{5} \right) \times 100$$

### Operational Tiers:
* **`EXCELLENT`** ($\ge 90$): Top-tier service; qualified for premium commission incentives.
* **`GOOD`** ($80 - 89$): Healthy operational standing; meets all baseline requirements.
* **`WATCH`** ($70 - 79$): Borderline performance; subjected to weekly SLA monitoring.
* **`AT_RISK`** ($< 70$): Underperforming; triggers warning and risk reserve escalation.
