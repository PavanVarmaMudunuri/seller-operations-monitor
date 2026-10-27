# Decision Log

## 1. Synthetic data instead of public data
Decision: Generate all operational data locally.

Why: The challenge permits synthetic data, and the business problem does not require
external data. This avoids licensing, privacy and redistribution ambiguity.

## 2. Python + Pandas + PostgreSQL-compatible SQL
Decision: Python is used for deterministic generation and business logic; SQL defines
the relational model and analytical views.

Trade-off: The reference implementation runs locally without requiring a database
server. PostgreSQL DDL is included for productionization.

## 3. Deterministic source-first generation
Decision: Generate parent records before children and derive totals/statuses from
source events.

Why: This protects referential integrity and makes outcomes reproducible.

## 4. Explicit event history
Decision: Seller status transitions are stored in seller_status_event rather than
silently overwriting history.

## 5. Ground truth separated from features
Decision: Deliberate anomalies are labelled in ground_truth/ground_truth.csv and
not exposed in normal operational tables.

Why: This permits objective evaluation without label leakage.

## 6. Reason codes instead of a single anomaly flag
The solution uses issue_type/expected_decision/severity in ground truth and
exception-oriented outputs so an operations user can understand what action is
expected.

## 7. Starter and full-scale modes
A small starter dataset is provided for fast verification. The full configuration
uses the requested 2,000 sellers, 20,000 listings, 100,000 orders and 10,000 disputes.

## 8. Intentional anomaly injection
Anomalies are injected after valid baseline data is generated. This prevents
accidental corruption from being confused with test scenarios.

## 9. Payout design
Payouts are calculated only from delivered, non-returned, eligible order lines after
the configured hold period and with applicable dispute deductions.

## 10. Known limitation
The reference implementation calculates payouts locally in Pandas. The included
PostgreSQL schema/views show the relational target architecture. A production version
would execute transformations and controls inside a database/ELT layer and add
workflow orchestration.
