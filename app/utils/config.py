import os
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")