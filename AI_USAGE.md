# AI Usage / Prompt History

This project was developed with LLM assistance. AI was used as an accelerator, not
as a substitute for understanding or validation.

## Tools used

- OpenAI ChatGPT / GPT-5.6 Luna
- Google Antigravity (Agentic AI Assistant)

## Prompt history

The following are the substantive prompts used in this project session.

### Prompt 1 — Business problem
> Business Context / Problem: Monitor seller service levels, order fulfillment,
> disputes, commissions and payout eligibility. Objective and Scope: Build a
> working solution for this end-to-end workflow ... [full candidate business
> specification supplied in the conversation].

Purpose: Convert the business specification into a concrete architecture,
data model, generator strategy, validation approach, anomaly model and dashboard.

### Prompt 2 — Implementation request
> develop the code and project and give me the zip file

Purpose: Produce the initial runnable project structure, synthetic generator,
rules, validation, SQL, tests, dashboard and documentation.

### Prompt 3 — Candidate checklist
> Candidate Project Submission Guidelines ... the above are the checklists and do
> satisfy all the cases

Purpose: Review the project against the 72-hour submission requirements and
identify/document gaps around execution, public GitHub, AI transparency,
reasoning, testing, assumptions, limitations and reproducibility.

### Prompt 4 — Verification, Anomaly Fixes & Metrics Alignment
> Business Context / Problem: do check all the exact and every line has been covered
> in this project or not do check and let me know / fix issues

Purpose: Conduct a rigorous line-by-line verification against the specification:
1. Identified and resolved missing anomaly case (`SUSPENDED_SELLER_CONTINUES_LISTING`) in injector logic.
2. Corrected net payout formula arithmetic (removed accidental duplicate commission deduction).
3. Fixed pandas `.join()` index alignment issue in `metrics.py` where seller metrics joined on integer index rather than `seller_id`, restoring accurate Orders and GMV metrics on the dashboard.
4. Expanded `data_dictionary.md` into comprehensive field-by-field specifications covering types, nullability, allowed values, units, uniqueness, validation constraints, and ER relationships.

## Where AI accelerated work

AI accelerated:
- Project scaffolding
- Initial schema design
- Data dictionary structure
- Synthetic-data generation patterns
- Business-rule pseudocode
- Validation/test scaffolding
- README/documentation structure
- Dashboard scaffolding

## What the candidate must personally review

Before submission, the candidate should personally:
1. Run the generator and inspect output.
2. Read and understand every core business rule.
3. Verify the five required anomaly cases.
4. Run the tests and investigate failures.
5. Verify reproducibility with two runs.
6. Inspect row counts and checksums.
7. Review SQL constraints and analytical views.
8. Review assumptions and limitations.
9. Make meaningful commits in the public Git repository.
10. Be able to explain the payout formula, seller score, anomaly design,
   lifecycle decisions and validation strategy.

## Transparency note

AI responses are not presented as proof that the implementation is correct.
Correctness is established through executable tests, generated-data inspection,
validation reports, deterministic checksums and candidate review.
