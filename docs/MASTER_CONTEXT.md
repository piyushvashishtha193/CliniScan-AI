# CliniScan AI: Master Context

> Single source of truth for this project. Every work session starts here.
> Owner: Piyush Vashishtha · Repo: github.com/piyushvashishtha193/CliniScan-AI
> Last updated: 7 Nov 2026

---

## 1. What this is

**CliniScan AI is a multilingual AI clinical scribe for Indian outpatient consultations.**

It turns a recorded doctor–patient conversation (English, Hindi or Hinglish) into:
- a speaker-labelled transcript (Doctor / Patient)
- a structured SOAP note, stored per patient
- answers to questions about that patient's uploaded lab reports, with citations

Patient identifiers are redacted before any text leaves the machine. Every stage is measured against public benchmarks.

### Problem
Doctors in Indian OPDs see dozens of patients a day and spend a large share of that time writing notes. Most consultations are code-mixed (Hindi + English), and most scribe tools are built for English only.

### Users
- **Primary:** an outpatient doctor who records a consultation and reviews the generated note.
- **Secondary:** the same doctor checking a returning patient's history and reports.

### Positioning
This is a portfolio project for **AI Engineer / Applied AI** roles. It's not a medical device. All output is a draft for clinician review.

---

## 2. Scope

### In scope

| # | Module | Output |
|---|---|---|
| 1 | Transcription | Faster-Whisper on GPU, with English, Hindi and Hinglish support |
| 2 | Diarization | PyAnnote segments aligned to Whisper word timestamps → Doctor/Patient labels |
| 3 | PHI redaction | Names, phone numbers, IDs and addresses masked before any LLM call |
| 4 | SOAP note | LLM → JSON validated against a Pydantic schema |
| 5 | Storage | SQLite: patients, consultations, notes, reports |
| 6 | Report Q&A (RAG) | Lab report PDFs → per-patient FAISS index → cited answers |
| 7 | Evaluation | WER, DER and note faithfulness on public datasets |
| 8 | Serving | FastAPI + Docker + public demo |

### Out of scope

Disease prediction, XGBoost, LIME, LangChain, MCP, mental-health forms, patient timeline charts, and real patient data. These were cut on purpose because they don't serve the core story. Tabular ML lives in a separate portfolio project.

---

## 3. Pipeline

```
Audio (upload / record)
  → Faster-Whisper        (text + word timestamps)
  → PyAnnote              (who spoke when)
  → Alignment             (assign each word to a speaker)
  → Role labelling        (SPEAKER_00 / 01 → Doctor / Patient)
  → PHI redaction         (mask identifiers)
  → LLM                   (SOAP note as validated JSON)
  → SQLite                (store against patient)

Lab report PDF
  → pdfplumber (OCR fallback for scans)
  → chunk + embed → FAISS (per patient)
  → question → retrieve → LLM answer with citations
```

---

## 4. Tech decisions

| Area | Choice | Why |
|---|---|---|
| STT | Faster-Whisper `small`, int8 on GPU | CTranslate2 is much faster than vanilla Whisper; `small` handles Hindi far better than `base` and still fits in 4 GB VRAM |
| Diarization | `pyannote/speaker-diarization-community-1` | Open, state-of-the-art, runs locally |
| Alignment | Word-timestamp overlap with diarization segments | Simple and explainable; errors are measurable through DER |
| Role labelling | LLM classifies speakers from content (who asks clinical questions) | Speaking order isn't a reliable signal |
| PHI redaction | Microsoft Presidio + custom Indian patterns (phone, Aadhaar-style IDs) | Standard tool with an extensible recogniser approach |
| LLM | Gemini Flash (default) · Ollama small model (local fallback) | Gemini: quality and free tier. Ollama: fully offline privacy mode. The trade-off is documented |
| Structured output | Pydantic schema + JSON mode, with retry on validation failure | The note can be stored, queried and checked |
| Storage | SQLite | Zero setup, single file, enough for one clinic |
| Embeddings | Small sentence-transformers model (CPU-friendly) | Laptop-friendly; quality is checked in evaluation |
| Vector store | FAISS | Fast, local, no server needed |
| API | FastAPI | Typed, async, auto-generated docs |
| UI | Streamlit (calls the services layer) | Already built and polished |
| Packaging | Docker | Reproducible setup and deployment |
| Deploy | Hugging Face Spaces (Docker, CPU, demo mode) | Streamlit Cloud can't run PyAnnote + Whisper |

### Hardware constraint
The dev machine has a **GTX 1650 with 4 GB of VRAM**. Every model choice has to fit in it. Local LLMs are limited to small quantised models. The deployed demo runs on CPU with short sample clips.

---

## 5. Evaluation

| Stage | Metric | Data | Tool |
|---|---|---|---|
| Transcription | WER | PriMock57 (mock consultation audio + transcripts) | `jiwer` |
| Diarization | DER | PriMock57 | `pyannote.metrics` |
| SOAP note | Faithfulness (% of note facts supported by transcript), hallucinated-fact count, ROUGE vs. reference | PriMock57 notes, ACI-Bench | LLM-as-judge + manual spot-check |
| Hinglish | WER, before/after improvements | Small self-recorded mock consultations (scripted, consented, no real patients) | `jiwer` |
| RAG | Faithfulness, context precision | ~30 hand-written Q&A pairs over sample reports | RAGAS |

Results go in `docs/EVALUATION.md` and the README.
**Only report numbers that were actually measured.**

---

## 6. Privacy and safety

- No real patient data, ever. Only mock and public datasets.
- PHI is redacted before any cloud LLM call. Local mode makes no network calls.
- Every note carries the line "AI-generated draft for clinician review".
- The prompt forbids inventing diagnoses, medications or findings, and the faithfulness metric checks this.
- Secrets live only in `.env`.

---

## 7. Architecture

```
cliniscan-ai/
├── app/
│   ├── core/          config, logging
│   ├── services/      transcription, diarization, alignment, redaction, llm, notes, rag
│   ├── db/            models, repository
│   ├── api/           FastAPI routes
│   └── schemas/       Pydantic models (SOAP note, consultation)
├── ui/                Streamlit app
├── eval/              evaluation scripts + results
├── tests/
├── docs/
├── Dockerfile
└── requirements.txt
```

Rule: the UI and the API both call `services/`. Neither contains model logic.

---

## 8. Current status (7 Nov 2026)

| Area | Status |
|---|---|
| Streamlit UI (upload + live record) | ✅ Done |
| Faster-Whisper on GPU (`base`) | ✅ Done; logic still inside `app.py` |
| Config via `.env` | ✅ Done |
| Gemini integration | 🟡 Works end to end, but outputs a free-text summary, not a SOAP JSON |
| Diarization | 🔴 Pipeline loader only |
| Redaction, SQLite, RAG, evaluation, API, Docker, deploy | 🔴 Not started |

### Known issues
- `requirements.txt` is saved as UTF-16 (from PowerShell `pip freeze >`), which breaks Docker/Linux. Regenerate it as UTF-8.
- `pyannote.audio` is missing from `requirements.txt`.
- `gemini.py` raises on import if the key is missing, which breaks tests.
- Hindi transcription is weak on `base`. Switch to `small` and test `language="hi"` against auto-detect.
- The live recording error hasn't been reproduced yet.
- `ROADMAP.md` and `PROGRESS.md` are stale (June). This file replaces the roadmap.

---

## 9. Build plan

| # | Milestone | Done when |
|---|---|---|
| M1 | Cleanup + transcription service | Requirements fixed; `transcription.py` extracted; Whisper `small` |
| M2 | Diarization + alignment + roles | UI shows a Doctor/Patient transcript |
| M3 | PHI redaction + SOAP JSON | Validated SOAP note shown in the UI; no PHI in the LLM input |
| M4 | SQLite + history | Consultations saved and viewable per patient |
| M5 | Evaluation | WER, DER and faithfulness numbers in `docs/EVALUATION.md` |
| M6 | Report RAG | Upload a PDF, ask a question, get a cited answer; RAGAS scores |
| M7 | FastAPI + Docker + tests | `docker run` serves the API and UI |
| M8 | Deploy + README + demo video | Live link; README leads with problem, results and demo |

**MVP = M1–M5.** That's the point to start applying.

---

## 10. Working mode

- Claude writes the code and explains each module: what it does, why it was chosen, and what the alternatives were.
- Piyush runs it on his laptop, tests it, reads the explanation, and commits.
- One meaningful commit per working piece.
- This file is updated at the end of every milestone (section 8 status + issues).
- No new features outside section 2 without updating this file first.

---

## 11. Interview prep: questions this project must answer

1. Why Faster-Whisper over the Whisper API, and why `small`?
2. How are words matched to speakers? What happens when people talk over each other?
3. How do you tell which speaker is the doctor?
4. Why redact PHI, and how do you know redaction works?
5. Gemini vs. a local LLM: what's the trade-off?
6. How do you stop the LLM from inventing a medication?
7. What are your WER, DER and faithfulness numbers, and what improved them?
8. Why SQLite, and when would you switch to Postgres?
9. How does the RAG part avoid answering from the wrong patient's reports?
10. What was the hardest bug?

---

## 12. Portfolio context

Project 1 of 5 (in build order): **CliniScan AI** → StudyTube AI (agentic RAG over Hinglish lectures) → UPI fraud detection + MLOps → AQI forecasting for Indian cities → LoRA fine-tune vs. base model.
Shared theme with StudyTube: **AI for Indian multilingual speech.**
