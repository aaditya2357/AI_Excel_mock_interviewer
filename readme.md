# Excel Mock Interviewer — PoC

A Gradio-based AI mock interviewer for Excel skills.  
This repo contains a runnable PoC: frontend (Gradio), a simple LangGraph-driven interviewer flow, local LLM wrapper, and a perplexity-based AI-content detector.

## What’s included
- `app.py` — Gradio UI and orchestration
- `src/graph.py` — graph workflow builder
- `src/interview_logic.py` — interview state machine and question set
- `src/local_llm_handler.py` — local LLM loading & generation
- `src/perplexity_detector.py` — perplexity-based AI detection
- `samples/` — sample transcripts & spreadsheets (add)
- `docs/design.md` — design doc (this repo)

## If you want to check the deploy link
https://huggingface.co/spaces/akunity2357/ai
