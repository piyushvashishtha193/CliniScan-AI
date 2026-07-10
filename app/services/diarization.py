from pyannote.audio import Pipeline

from app.utils.config import HUGGINGFACE_TOKEN


def load_diarization_pipeline():
    """
    Load and return the pretrained PyAnnote speaker diarization pipeline.
    """
    return Pipeline.from_pretrained(
        "pyannote/speaker-diarization-community-1",
        token=HUGGINGFACE_TOKEN,
    )