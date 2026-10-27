# Seller Operations Monitor

A reproducible synthetic marketplace operations platform for monitoring:

- Seller service levels
- Product listings
- Orders and multi-seller fulfillment
- Shipment/delivery SLAs
- Returns and reviews
- Disputes and chargebacks
- Commission and reserve rules
- Payout eligibility and reconciliation
- Business exceptions/anomalies
- Ground-truth evaluation
- Data quality and reproducibility

## Architecture

Synthetic source data -> deterministic business rules -> labelled anomaly injection ->
validation -> analytics -> dashboard-ready outputs.

## Quick start

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python scripts/run_pipeline.py --config configs/starter.yaml
```

For the full requested scale:

```bash
python scripts/run_pipeline.py --config configs/full.yaml
```

Outputs are written under `data/exports/`, `ground_truth/`, and `reports/`.

## Reproducibility

The default full-data seed is `20261022`. Run the pipeline twice with the same
configuration and seed; `reports/reproducibility.json` records row counts and
SHA-256 checksums for the generated CSV outputs.

## Deliberate exception classes

The pipeline injects labelled cases for:

1. Payout before delivery/hold release
2. Commission applied twice
3. Suspended seller continues listing
4. Dispute not deducted
5. Payout total does not equal payout lines

The ground truth is stored separately and is never included in the normal input features.

## Project layout

- `configs/` - scale and business-rule parameters
- `docs/` - data dictionary and business rules
- `sql/` - PostgreSQL schema and analytical views
- `src/` - generators, rules, anomaly injection, validation and analytics
- `tests/` - automated tests
- `dashboard/` - Streamlit dashboard
- `data/exports/` - generated CSVs
- `ground_truth/` - known anomaly labels
- `reports/` - validation, metrics and reproducibility reports
