import os
from pathlib import Path

from dotenv import load_dotenv
import google.genai as genai

# Load .env from project root (backend/factory -> backend -> root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# --- CONFIGURATION ---
_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
_CLIENT = genai.Client(api_key=_API_KEY) if _API_KEY else None
MODEL = "gemini-2.0-flash"


def query_llm(system_prompt: str, user_prompt: str) -> str | None:
    """
    Sends a request to Gemini and returns the text response.
    """
    if not _CLIENT:
        print("❌ No GEMINI_API_KEY / GOOGLE_API_KEY set")
        return None
    try:
        combined = f"{system_prompt}\n\n{user_prompt}"
        response = _CLIENT.models.generate_content(
            model=MODEL,
            contents=combined,
        )
        return response.text
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return None


def save_artifact(path: str, content: str) -> None:
    """
    Writes the code artifact to the disk.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"💾 Artifact Saved: {path}")
