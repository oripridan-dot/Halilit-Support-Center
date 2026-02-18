import os
from pathlib import Path

from dotenv import load_dotenv
import openai

# Load .env from project root (backend/factory -> backend -> root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# --- CONFIGURATION ---
CLIENT = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o"  # Or "claude-3-5-sonnet-20240620" if using Anthropic

def query_llm(system_prompt, user_prompt):
    """
    Sends a request to the LLM and returns the text response.
    """
    try:
        response = CLIENT.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1  # Low temperature for precise code generation
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return None

def save_artifact(path, content):
    """
    Writes the code artifact to the disk.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"💾 Artifact Saved: {path}")
