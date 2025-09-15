AI-Powered Excel Mock Interviewer — Design Document

## 1. Problem Statement
Manual Excel technical screening is slow, inconsistent, and a hiring bottleneck. We need an automated interviewer that simulates a human interviewer, evaluates candidate answers (including spreadsheet uploads/formula checks), and produces a constructive feedback report.

## 2. Goals & Success Metrics
- Replace initial manual screens with an automated assessment.
- Metrics: accuracy (agreement with SME on deterministic tasks) ≥ 90%, inter-rater correlation (system vs SME) ≥ 0.8, average screening time ≤ 5 minutes per candidate.

## 3. Personas
- Candidate: completes interview, uploads spreadsheets, receives feedback.
- Hiring Manager: receives candidate report, recommended role-fit.
- SME / Reviewer: audits flagged evaluations and refines rubrics.

## 4. High-level Architecture
- Frontend: Gradio (fast prototype) for production.
- LLM Layer: local or hosted instruction-following model for open-ended evaluation + report writing.
- Deterministic Evaluator: Python (pandas / openpyxl) for file/formula validation.
- State store: Redis for session; Postgres for transcripts/reports.

## 5. Interview Flow
1. Candidate starts session → system greets and explains.
2. System asks Q1 
3. Candidate answers in textbox.
4. Deterministic checks run (if applicable). LLM grades open answers.
5. System returns evaluation, stores evaluation, routes to next question or final report.
6. Final report generated.

## 6. Evaluation Strategy
- **Hybrid**: deterministic checks (60%), LLM semantic scoring (20%), heuristics/UX (20%).
- Deterministic checks: run candidate formula or transformation on seeded test-cases.
- LLM checks: rate clarity, approach, suggestions.
- Low-confidence answers flagged for SME review (active learning).

## 7. Cold-start Strategy
- SME-authored canonical Q&A and spreadsheet seeds.
- Programmatic synthetic spreadsheets with controlled patterns.
- Self-play: LLMs generate candidate answers of different skill levels.
- Human-in-the-loop: correct model outputs until confidence improves.

## 8. Security & Privacy
- Consent before recording or storing uploads.
- PII detection & masking in uploaded sheets.
- Retention policy & secure deletion API.
- Secrets via environment variables, not in repo.

## 9. Deployment & Scaling
- Containerize backend + LLM service.
- Start with a single node on Render / Cloud Run; move to autoscaling with GPU nodes if using large local models.
- Use smaller hosted LLM for production scoring to reduce infra burden.

## 10. Future Enhancements
- Add interactive spreadsheet editor and timed tasks.
- Integrate Power Query / VBA runnable sandbox for advanced tasks.
- Continuous improvement loop with SME review queue.

