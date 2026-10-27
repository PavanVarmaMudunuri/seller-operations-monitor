# Validation Strategy and Evaluation Framework

This document outlines the validation procedures, integrity checks, and evaluation methodology used to verify the Seller Operations Monitor system.

---

## 1. Relational and Structural Validation

The validation suite in `src/validation/validate.py` executes structural checks across all generated datasets:

* **Primary Key Uniqueness**: Confirms that every primary key column across all 12 tables contains zero duplicates.
* **Foreign Key Referential Integrity**: Validates that all relational child references point to existing parent identifiers:
  * Catalog listings point to existing sellers.
  * Orders point to valid customers.
  * Order lines point to valid orders, listings, and sellers.
  * Fulfillment records map 1:1 with existing order lines.
  * Disputes reference valid orders and order lines.
  * Payout records map to registered sellers.
  * Payout lines reference active payout headers and delivered order lines.
* **Domain Range Constraints**: Verifies that stock quantities, unit prices, review stars (1 to 5), and commission rates (0.0 to 1.0) strictly adhere to expected business bounds.
* **Order Line Arithmetic Reconciliation**: Confirms that line totals mathematically balance:
  $$\text{line\_total} == (\text{quantity} \times \text{unit\_price}) - \text{discount\_amount}$$

---

## 2. Business Logic and Exception Validation

The validation engine monitors both standard operations and deliberate anomalies:

* **Seller Eligibility**: Confirms that sellers suspended in baseline generation do not receive standard disbursements.
* **Dispute Withholding**: Verifies that active chargebacks block payout creation until resolution.
* **Controlled Reconciliation Mismatches**: The pipeline checks that the header payout total equals the sum of its payout lines. Because anomaly #5 deliberately introduces a ₹100 discrepancy, the validation summary explicitly flags and reports this variance rather than silently suppressing it:
  $$\text{payout.reconciliation\_clean} = \text{False} \quad (\text{Observed intentional mismatches})$$

---

## 3. Evaluation and Ground Truth Benchmarking

To evaluate how effectively monitoring rules and detection models perform, predictions can be benchmarked against `ground_truth/ground_truth.csv`:

* **Precision**: $\frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$ (Assesses whether flagged exceptions are genuine).
* **Recall**: $\frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$ (Assesses whether all injected anomalies were surfaced).
* **F1-Score**: $\frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$ (Harmonic mean of detection accuracy).

Because ground-truth labels remain strictly segregated from feature inputs, this dataset serves as a benchmark for automated fraud detection models and exception alert systems.

---

## 4. Deterministic Reproducibility

Reproducibility is enforced via:
* **Seed Locking**: Fixed NumPy and Python pseudo-random number generator seed (`20261022`).
* **Cryptographic Hashes**: SHA-256 digests and exact row counts are generated for every exported table and saved to `reports/reproducibility.json`.

### Verifying Reproducibility Locally:
Run the pipeline twice with identical parameters:
```bash
python scripts/run_pipeline.py --config configs/starter.yaml
python scripts/compare_runs.py data/exports/ data/exports_backup/
```
The comparison script checks file checksums and confirms whether the outputs are bit-for-bit identical.
