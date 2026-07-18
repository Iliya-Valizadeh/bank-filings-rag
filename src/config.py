"""Config: paths, models, retrieval knobs."""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
INDEX_DIR = ROOT / "index"
REPORTS = ROOT / "reports"

EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TOP_K = int(os.getenv("TOP_K", "5"))
