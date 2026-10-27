# Validation and Evaluation

## Structural validation

The pipeline checks:
- Primary-key uniqueness
- Foreign-key integrity
- Positive quantities/prices
- Enum/range constraints
- Order-line arithmetic
- Payout reconciliation

## Business validation

The intended controls cover:
- Seller suspension vs active listings
- Delivery and hold windows
- Returns
- Open disputes
- Commission calculation
- Reserve calculation
- Payout reconciliation

## Evaluation

The anomaly injector creates an independent ground-truth table. The next evaluation
layer can compare detected exception IDs/types with ground truth using precision,
recall and F1.

The repository's baseline validation deliberately permits expected business-anomaly
failures in the final reconciliation report. This is intentional: the system must
surface those exceptions rather than silently repair them.

## Reproducibility

The generator uses seed `20261022` by default. `reports/reproducibility.json`
contains SHA-256 checksums and row counts for exported files.

To verify determinism, run the same configuration twice and compare the generated
CSV checksums.

## Verification commands

```bash
python scripts/run_pipeline.py --config configs/starter.yaml
python -m pytest -q
```

Full scale:

```bash
python scripts/run_pipeline.py --config configs/full.yaml
```

Dashboard:

```bash
streamlit run dashboard/app.py
```
