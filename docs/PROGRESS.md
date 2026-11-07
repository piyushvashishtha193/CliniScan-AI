# CliniScan AI: Progress Log

Short, dated record of what got done. The plan lives in [MASTER_CONTEXT.md](MASTER_CONTEXT.md).

---

### Nov 2026
- Final scope locked in `MASTER_CONTEXT.md`: multilingual clinical scribe with diarization, PHI redaction, SOAP JSON, report RAG, evaluation, FastAPI, Docker, CI and tracing
- Cut out of scope: disease prediction, XGBoost/LIME, mental-health forms, patient timeline
- Old `ROADMAP.md` removed

### Jul 2026
- Gemini service (`app/services/gemini.py`) wired into the app: transcript → structured clinical summary
- Diarization service started: PyAnnote Community-1 pipeline loader
- Secure config via `.env` + `python-dotenv` (`app/utils/config.py`)
- Faster-Whisper on GPU (CUDA, int8_float16) with timestamped transcript
- Fixed the Windows CUDA DLL path issue for cuBLAS/cuDNN
- Audio upload + live recording in Streamlit, using temp-file handling

### Jun 2026
- Repo, Git/GitHub workflow, virtual environment, README, licence
- First Streamlit app with a custom theme and clinical UI
