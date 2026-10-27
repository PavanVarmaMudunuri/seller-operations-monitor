# Business Rules

## Seller lifecycle

`PENDING -> ACTIVE -> SUSPENDED -> REACTIVATED`

A seller may be suspended for poor service, risk, or unresolved disputes.
Historical status changes are retained in `seller_status_events.csv`.

## Listing lifecycle

`DRAFT -> ACTIVE -> PAUSED -> DISCONTINUED`

A suspended seller must not create or reactivate a listing. Deliberate negative
cases are labelled in ground truth.

## Fulfillment

Each order line normally creates one fulfillment record. Multi-seller orders
are split naturally because order lines retain seller IDs.

Shipment SLA:
- `ON_TIME`: actual ship date <= promised ship date
- `LATE`: 1-2 days late
- `SEVERELY_LATE`: >2 days late

## Disputes

Open disputes reduce payout eligibility. Chargebacks are deducted from payout
when the dispute is financially applicable.

## Commission

Commission is calculated from the commission base using the effective
commission rule. A deliberately injected duplicate commission is flagged.

## Reserve

- New seller: 15%
- Established seller: 5%
- High-risk seller: 25%

## Payout eligibility

A payout line is eligible only when:
1. Fulfillment is delivered.
2. Delivery date + hold days <= payout calculation date.
3. The seller is not suspended.
4. The order line is not returned.
5. There is no unresolved financially applicable dispute.

## Payout reconciliation

`Payout.total_amount == SUM(PayoutLine.net_payout_amount)`

A deliberate mismatch is injected only after a valid payout has been generated.

## Service score

`40% on-time shipment + 25% delivery success + 20% dispute-free rate + 15% normalized rating`

Bands:
- >= 90: EXCELLENT
- >= 80: GOOD
- >= 70: WATCH
- < 70: AT_RISK
