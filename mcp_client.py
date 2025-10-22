import requests
import dateparser
from gcalendar import create_event
import datetime

BASE_URL = "http://127.0.0.1:8000"

# ---------------- Quotes ----------------
def get_quote(query: str = None, k: int = 3) -> str:
    params = {"q": query, "k": k} if query else {}
    resp = requests.get(f"{BASE_URL}/quotes/search", params=params)
    resp.raise_for_status()
    quotes = resp.json()
    # Convert to readable string
    return "\n\n".join([f"{q['text']} — {q.get('author','Unknown')}" for q in quotes])

# ---------------- Affirmations ----------------
def fetch_affirmations(count: int = 3) -> str:
    resp = requests.get(f"{BASE_URL}/affirmations", params={"count": count})
    resp.raise_for_status()
    data = resp.json()
    return "\n".join(data["affirmations"])

# ---------------- Journal prompts ----------------
def fetch_journal_prompt() -> str:
    resp = requests.get(f"{BASE_URL}/journal/prompt")
    resp.raise_for_status()
    return resp.json()["prompt"]

def schedule_reminder(text: str) -> str:
    event_time = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
    if not event_time:
        return "I couldn't understand the time. Can you rephrase?"

    link = create_event(text, event_time, duration_minutes=20)

    # Fetch meditation or journaling prompt dynamically from MCP server
    try:
        resp = requests.get(f"{BASE_URL}/journal/prompt")  # Can be changed to a dedicated endpoint
        resp.raise_for_status()
        guidance = resp.json().get("prompt", "Take a moment to breathe and relax.")
    except Exception:
        guidance = "Take a moment to breathe and relax."

    return f"✅ Event created! {guidance}\nYou can view it here: {link}"

# ---------------- Breathing exercises ----------------
def suggest_breathing(duration_seconds: int = 60, pattern: str = "box") -> str:
    payload = {"duration_seconds": duration_seconds, "pattern": pattern}
    resp = requests.post(f"{BASE_URL}/breathing/suggest", json=payload)
    resp.raise_for_status()
    data = resp.json()
    return "\n".join(data["steps"])
