# interactive_mcp_chat.py
from copilot_proxy import handle_copilot_query

response = handle_copilot_query("Give me a quote about courage")
# print(response)

response = handle_copilot_query("Guide me with breathing")
# print(response)

from mcp_client import (
    chat_with_bot,
    get_quote,
    box_breathing,
    suggest_breathing,
    get_random_quote,
)

def main():
    print("=== Welcome to MCP Chat ===")
    print("Type your question, 'quote', or 'breathing'. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Simple commands for quick testing
        if user_input.lower() == "quote":
            query = input("Enter keyword for quote search: ").strip()
            try:
                quote = get_quote(query) if query else get_random_quote()
            except Exception as e:
                print(f"Error fetching quote: {e}\n")
                continue

            print(f"MCP Quote: {quote.get('text', 'No quote found')} — {quote.get('author', '')}\n")
            continue

        if user_input.lower() == "breathing":
            pattern = input("Enter breathing pattern (box/4-7-8/coherent): ").strip().lower()
            duration_str = input("Enter duration in seconds: ").strip()
            try:
                duration = int(duration_str)
            except Exception:
                duration = 60

            if pattern == "box":
                try:
                    exercise = box_breathing(duration)
                except Exception as e:
                    print(f"Error requesting breathing plan: {e}\n")
                    continue
            else:
                # fallback to box if unknown pattern
                if pattern not in ("4-7-8", "4-7-8", "coherent"):
                    pattern = "box"
                try:
                    exercise = suggest_breathing(duration, pattern)
                except Exception as e:
                    print(f"Error requesting breathing plan: {e}\n")
                    continue

            print(f"MCP Breathing Steps: {exercise.get('steps', [])}\n")
            continue

        # Default: send input to chatbot
        try:
            response = chat_with_bot(user_input)
            print(f"MCP Bot: {response.get('response', 'No response')}\n")
        except Exception as e:
            print(f"Error contacting MCP bot: {e}\n")
            continue

if __name__ == "__main__":
    main()
