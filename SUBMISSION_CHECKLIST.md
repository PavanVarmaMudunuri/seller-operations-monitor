# Submission Checklist

## 01 MAKE IT RUN

- [ ] Clone the public repository.
- [ ] Create a clean Python environment.
- [ ] `pip install -r requirements.txt`
- [ ] Run starter pipeline.
- [ ] Run `python -m pytest -q`.
- [ ] Run full pipeline.
- [ ] Launch Streamlit dashboard.
- [ ] Inspect generated CSVs and reports.
- [ ] Verify the five required exception classes.

## 02 SHOW YOUR WORK

- [ ] Create a new dedicated PUBLIC GitHub repository.
- [ ] Push this project.
- [ ] Use meaningful commits, not one opaque commit.
- [ ] Keep the repository editable until the deadline.
- [ ] Add the actual repository URL to the final submission email/form.

Suggested commit sequence:
1. `docs: define business rules and data model`
2. `feat: add deterministic synthetic data generator`
3. `feat: add payout and commission engine`
4. `feat: add labelled anomaly scenarios`
5. `test: add integrity and reconciliation validation`
6. `feat: add analytics and dashboard`
7. `docs: add AI usage and submission notes`

## 03 USE LLMS TRANSPARENTLY

- [ ] Keep `AI_USAGE.md`.
- [ ] Add every prompt used with every AI tool.
- [ ] Disclose the tool name.
- [ ] State what AI accelerated.
- [ ] State what you personally reviewed/changed/validated.
- [ ] Do not claim AI-generated code was independently correct without testing.

## 04 MAKE REASONING VISIBLE

- [ ] Read `docs/decision_log.md`.
- [ ] Read `docs/business_rules.md`.
- [ ] Read `docs/data_dictionary.md`.
- [ ] Read `docs/validation_and_evaluation.md`.
- [ ] Be ready to explain limitations and trade-offs.

## Safety / repository hygiene

- [ ] No passwords, API keys or tokens.
- [ ] No customer PII.
- [ ] No proprietary source code.
- [ ] No private datasets.
- [ ] Synthetic data only unless a properly licensed public dataset is intentionally added.

## Important

The project should be treated as individual work. Before submission, personally
review and understand the implementation. Do not submit code you cannot explain.
