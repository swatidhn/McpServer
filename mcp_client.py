import requests
import random

BASE_URL = "http://127.0.0.1:8000"

# -----------------------
# Quotes API
# -----------------------
def get_quote(query: str = None) -> str:
    """
    Fetch a single quote from MCP server and return as a string.
    """
    params = {}
    if query:
        params["q"] = query
    try:
        resp = requests.get(f"{BASE_URL}/quotes/search", params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return "🌸 Stay inspired! A quote will appear soon."

        if isinstance(data, list):
            top = data[0]
        elif isinstance(data, dict) and "value" in data:
            top = data["value"][0]
        else:
            return "🌸 Stay inspired! A quote will appear soon."

        text = top.get("text", "")
        author = top.get("author")
        return f'"{text}"' + (f" — {author}" if author else "")
    except Exception as e:
        return f"⚠️ Could not fetch a quote ({e})"


def get_random_quote() -> str:
    """Return a random quote string."""
    try:
        resp = requests.get(f"{BASE_URL}/quotes/search", params={"q": "a", "k": 10}, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            top = random.choice(data)
            text = top.get("text", "")
            author = top.get("author")
            return f'"{text}"' + (f" — {author}" if author else "")
        return "🌸 Stay inspired! A quote will appear soon."
    except Exception as e:
        return f"⚠️ Could not fetch a random quote ({e})"


# -----------------------
# Breathing Exercises API
# -----------------------
def suggest_breathing(duration_seconds: int = 60, pattern: str = "box") -> str:
    """
    Return a breathing exercise plan as a string.
    """
    try:
        resp = requests.post(
            f"{BASE_URL}/breathing/suggest",
            json={"duration_seconds": duration_seconds, "pattern": pattern},
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
        steps = data.get("steps", [])
        if not steps:
            return "⚠️ Could not generate breathing exercise."
        return f"💨 Breathing exercise ({pattern}, {duration_seconds}s):\n" + "\n".join(steps)
    except Exception as e:
        return f"⚠️ Could not fetch a breathing plan ({e})"


def box_breathing(duration_seconds: int = 60) -> str:
    return suggest_breathing(duration_seconds, "box")


def four_seven_eight_breathing(duration_seconds: int = 60) -> str:
    return suggest_breathing(duration_seconds, "4-7-8")


# -----------------------
# Affirmations API
# -----------------------
def fetch_affirmations() -> str:
    """
    Fetch affirmations from MCP server.
    """
    try:
        resp = requests.get(f"{BASE_URL}/affirmations", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            return random.choice(data)
        return "💖 You are enough, just as you are."
    except Exception as e:
        return f"⚠️ Could not fetch affirmations ({e})"


# -----------------------
# Journal Prompt API
# -----------------------
def fetch_journal_prompt() -> str:
    """
    Fetch a journaling prompt from MCP server.
    """
    try:
        resp = requests.get(f"{BASE_URL}/journal/prompt", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, str):
            return data
        return "📝 Write down one thing you are grateful for today."
    except Exception as e:
        return f"⚠️ Could not fetch journal prompt ({e})"


# -----------------------
# Chatbot API (if implemented)
# -----------------------
def chat_with_bot(message: str) -> str:
    """
    Return a string response from MCP chatbot.
    """
    try:
        resp = requests.post(f"{BASE_URL}/chat", json={"message": message}, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("bot_response") or "⚠️ No response from chatbot."
    except Exception as e:
        return f"⚠️ Chatbot error ({e})"


# -----------------------
# Quick Test
# -----------------------
if __name__ == "__main__":
    print("Quote about doubts:")
    print(get_quote("doubts"))

    print("\nRandom quote:")
    print(get_random_quote())

    print("\nBox Breathing 60s:")
    print(box_breathing())

    print("\n4-7-8 Breathing 60s:")
    print(four_seven_eight_breathing())

    print("\nAffirmation:")
    print(fetch_affirmations())

    print("\nJournal Prompt:")
    print(fetch_journal_prompt())

    print("\nChatbot test:")
    print(chat_with_bot("Hello MCP!"))
