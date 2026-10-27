# Architectural Decision Log

This document records the key architectural choices, engineering trade-offs, and design rationale adopted during the development of the Seller Operations Monitor platform.

---

## 1. Local Deterministic Generation vs. External Public Datasets

* **Decision**: Generate all master entities and transactional lifecycles synthetically via an in-memory, seed-controlled generator rather than ingesting third-party web scrapes or public ecommerce dumps.
* **Rationale**: Public e-commerce datasets (e.g. Olist or Amazon dumps) frequently lack synchronized operational tables, such as rolling risk reserves, multi-seller split fulfillment lines, chargeback resolution states, and deliberate anomalous disbursements. Synthetic generation provides 100% referential integrity, guarantees deterministic reproducibility across machines, and avoids data privacy (PII) or licensing ambiguity.

---

## 2. Python / Pandas Engine with PostgreSQL Target DDL

* **Decision**: Use Python and Pandas for data synthesis and in-memory business calculations, accompanied by PostgreSQL-compatible DDL schemas (`sql/001_create_tables.sql`) and analytical views (`sql/004_analytics_views.sql`).
* **Trade-off**: Running calculations in Python ensures zero setup friction for evaluators—the entire pipeline runs locally out of the box without requiring a live PostgreSQL instance. The included SQL scripts demonstrate the exact relational schema, constraints, and views required for production deployment in an enterprise data warehouse or ELT pipeline.

---

## 3. Strict Parent-First Relational Generation

* **Decision**: Construct master parent tables (`seller`, `customer`, `commission_rule`) first, followed by catalog listings, orders, split order lines, logistics fulfillments, disputes, and finally settlement lines.
* **Rationale**: This strictly prevents dangling references or orphan records. Every child event directly inherits valid parent identifiers, ensuring 100% foreign key integrity across the operational graph.

---

## 4. Immutable Event History vs. In-Place Status Mutation

* **Decision**: Implement an explicit `seller_status_event` ledger to record every change in merchant standing (`PENDING` $\rightarrow$ `ACTIVE` $\rightarrow$ `SUSPENDED`).
* **Rationale**: In real-world financial systems, updating a seller's status in-place destroys auditability. Recording state changes with timestamps and operational reasons preserves complete history for dispute investigations and compliance audits.

---

## 5. Strict Separation of Ground-Truth Anomaly Labels

* **Decision**: Output all known anomaly labels into a dedicated, isolated file (`ground_truth/ground_truth.csv`) rather than adding an `is_anomaly` column directly into operational CSV exports.
* **Rationale**: Adding anomaly flags directly into operational data causes label leakage, which undermines the objectivity of evaluation metrics. Keeping ground truth completely segregated enables realistic downstream audits and machine-learning anomaly detection tests.

---

## 6. Actionable Reason Codes vs. Binary Anomaly Flags

* **Decision**: Model anomalies with explicit `issue_type`, `expected_decision` (`BLOCK`, `REVIEW`, `HOLD`), and `severity` (`HIGH`, `CRITICAL`) classifications.
* **Rationale**: In an actual operations center, a binary "anomaly=true" flag provides insufficient context. Operational personnel require specific decision directives—such as immediately blocking a payout batch with mismatched totals or reviewing a duplicate fee assessment.

---

## 7. Dual-Configuration Scale Strategy

* **Decision**: Provide both a lightweight starter configuration (`configs/starter.yaml`) and a full production configuration (`configs/full.yaml`).
* **Rationale**: Enables rapid end-to-end smoke testing, test execution, and dashboard validation in under 5 seconds, while retaining the capability to generate the full requested volume of 2,000 sellers, 20,000 listings, 100,000 orders, and 10,000 disputes.

---

## 8. Post-Baseline Anomaly Injection Pattern

* **Decision**: Synthesize clean, 100% valid baseline operational records first, and then apply deliberate mutations based on the anomaly configuration.
* **Rationale**: Injecting anomalies after generating clean data ensures that exceptions represent intentional, controlled business scenarios rather than accidental noise or corrupt synthetic distributions.

---

## 9. Conservative Payout Disbursement Window

* **Decision**: Enforce a mandatory 7-day post-delivery hold period before any order line becomes eligible for payout line creation.
* **Rationale**: Customer dispute and return requests predominantly occur within the first week of physical delivery. Enforcing this hold window protects marketplace liquidity and minimizes post-settlement clawbacks.

---

## 10. Known Assumptions and Limitations

* **Batch vs. Streaming Processing**: The reference implementation calculates payouts and metrics as a deterministic batch process. A live enterprise implementation would use event-streaming platforms (such as Kafka or Google Cloud Pub/Sub) to transition seller statuses and fulfillment events in real time.
* **Dispute Adjudication Workflow**: Disputes are currently modeled in binary `OPEN` or `RESOLVED` states. A production platform would typically feature a multi-stage adjudication workflow involving merchant evidence submission, buyer appeals, and banking chargeback arbitrations.
