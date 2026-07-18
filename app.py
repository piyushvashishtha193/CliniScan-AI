import tempfile
import os
from app.services.gemini import generate_clinical_summary

# Point Windows to the CUDA libraries installed via pip, so they load
# every time this script runs — no manual PATH setup needed anymore.
venv_path = os.path.dirname(os.path.abspath(__file__))
cublas_path = os.path.join(venv_path, "venv", "Lib", "site-packages", "nvidia", "cublas", "bin")
cudnn_path = os.path.join(venv_path, "venv", "Lib", "site-packages", "nvidia", "cudnn", "bin")
os.environ["PATH"] = cublas_path + os.pathsep + cudnn_path + os.pathsep + os.environ["PATH"]

import streamlit as st
from faster_whisper import WhisperModel

st.set_page_config(page_title="CliniScan AI", page_icon="🩺", layout="centered")

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.brand-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.2rem;
    color: #10241F;
    margin-bottom: 0;
}
.brand-sub {
    color: #5C6F69;
    font-size: 0.95rem;
    margin-top: 0.2rem;
    margin-bottom: 1.4rem;
}

.waveform {
    display: flex;
    align-items: center;
    gap: 3px;
    height: 28px;
    margin: 0.4rem 0 1.6rem 0;
}
.waveform span {
    display: inline-block;
    width: 3px;
    background: #0E7C6B;
    border-radius: 2px;
    animation: pulse 1.2s ease-in-out infinite;
}
.waveform span:nth-child(odd) { background: #E8623D; }
@keyframes pulse {
    0%, 100% { height: 6px; }
    50% { height: 26px; }
}

.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #0E7C6B;
    border-bottom: 1px solid #E1E8E5;
    padding-bottom: 0.5rem;
    margin: 1.6rem 0 1rem 0;
}

[data-testid="stFileUploader"], [data-testid="stAudioInput"] {
    background: #FFFFFF;
    border: 1px solid #E1E8E5;
    border-radius: 10px;
    padding: 0.6rem;
}

.transcript-card {
    background: #FFFFFF;
    border: 1px solid #E1E8E5;
    border-left: 3px solid #0E7C6B;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
}
.transcript-time {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #0E7C6B;
    background: #E4F3EF;
    padding: 2px 8px;
    border-radius: 4px;
    margin-right: 0.6rem;
}
.transcript-text {
    color: #10241F;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<p class="brand-title">🩺 CliniScan AI</p>', unsafe_allow_html=True)
st.markdown('<p class="brand-sub">AI-powered clinical documentation, generated from your voice.</p>', unsafe_allow_html=True)
st.markdown("""
<div class="waveform">
    <span style="animation-delay:0s"></span><span style="animation-delay:0.1s"></span>
    <span style="animation-delay:0.2s"></span><span style="animation-delay:0.3s"></span>
    <span style="animation-delay:0.4s"></span><span style="animation-delay:0.5s"></span>
    <span style="animation-delay:0.6s"></span><span style="animation-delay:0.7s"></span>
    <span style="animation-delay:0.8s"></span><span style="animation-delay:0.9s"></span>
</div>
""", unsafe_allow_html=True)

# ---------- Model ----------
@st.cache_resource
def load_model():
    return WhisperModel("base", device="cuda", compute_type="int8_float16")

model = load_model()

# ---------- Intake ----------
st.markdown('<p class="section-label">Consultation Intake</p>', unsafe_allow_html=True)

tab_upload, tab_record = st.tabs(["📁 Upload Audio", "🎙️ Record Live"])

audio_source = None

with tab_upload:
    uploaded_file = st.file_uploader("Upload consultation audio", type=["wav", "mp3", "m4a"], label_visibility="collapsed")
    if uploaded_file is not None:
        audio_source = uploaded_file

with tab_record:
    recorded_audio = st.audio_input("Record consultation")
    if recorded_audio is not None:
        audio_source = recorded_audio

# ---------- Transcription ----------
if audio_source is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(audio_source.getbuffer())
        temp_audio_path = temp_file.name

    st.audio(audio_source)

    with st.spinner("Transcribing consultation..."):
        segments, info = model.transcribe(temp_audio_path)
        segments = list(segments)

    # Create one complete transcript for Gemini
    full_transcript = " ".join(
        segment.text.strip()
        for segment in segments
    )

    # Generate AI clinical summary
    with st.spinner("Generating clinical summary..."):
        clinical_summary = generate_clinical_summary(full_transcript)

    os.remove(temp_audio_path)

    # Display transcript
    st.markdown(
        '<p class="section-label">Transcript</p>',
        unsafe_allow_html=True
    )

    for segment in segments:
        st.markdown(
            f"""
            <div class="transcript-card">
                <span class="transcript-time">
                    {segment.start:.1f}s – {segment.end:.1f}s
                </span>
                <span class="transcript-text">
                    {segment.text}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Display AI summary
    st.markdown(
        '<p class="section-label">Clinical Summary</p>',
        unsafe_allow_html=True,
    )

    st.markdown(clinical_summary)