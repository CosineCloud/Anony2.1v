import os
import json
import logging
from openai import OpenAI

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === CONFIGURATION ===

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",  # Keep this secure
)

# Base directory for memory files
MEMORY_DIR = "ai_memory"

# Maximum memory file size in bytes (1MB)
MAX_MEMORY_SIZE = 1024 * 1024  # 1MB

# === MEMORY HANDLING ===

def get_memory_file_path(user_id):
    """Get the path to the memory file for a specific user."""
    return os.path.join(MEMORY_DIR, f"{user_id}.json")

def load_chat_history(user_id=None):
    """Loads chat history from a user-specific JSON memory file."""
    # For backward compatibility with the main function
    if user_id is None:
        # Use the old MEMORY_FILE for the main function
        memory_file = "123content.json"
    else:
        memory_file = get_memory_file_path(user_id)
    
    if os.path.exists(memory_file):
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading chat history for user {user_id}: {e}")
            return []
    return []

def save_to_memory(chat_history, user_id=None):
    """
    Saves the chat history to the user-specific JSON memory file.
    Checks file size and resets if it exceeds the limit.
    
    Returns:
        bool: True if memory was reset due to size limit, False otherwise
    """
    # For backward compatibility with the main function
    if user_id is None:
        # Use the old MEMORY_FILE for the main function
        memory_file = "123content.json"
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, indent=2)
        return False
    
    memory_file = get_memory_file_path(user_id)
    os.makedirs(os.path.dirname(memory_file), exist_ok=True)
    
    # First, try to write to a temporary file to check the size
    temp_file = f"{memory_file}.temp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, indent=2)
    
    # Check file size
    file_size = os.path.getsize(temp_file)
    logger.info(f"Memory file size for user {user_id}: {file_size} bytes")
    
    if file_size > MAX_MEMORY_SIZE:
        logger.warning(f"Memory file for user {user_id} exceeds size limit. Resetting.")
        # Keep only the system message and the last 5 exchanges (10 messages)
        if len(chat_history) > 11:  # System message + 5 exchanges
            reset_history = [chat_history[0]]  # Keep the system message
            reset_history.extend(chat_history[-10:])  # Keep the last 5 exchanges
            chat_history = reset_history
        
        # Write the truncated history
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, indent=2)
        
        # Remove the temp file
        os.remove(temp_file)
        return True
    else:
        # If size is OK, rename the temp file to the actual file
        if os.path.exists(memory_file):
            os.remove(memory_file)
        os.rename(temp_file, memory_file)
        return False

# === BELLA'S PERSONALITY ===

bella_intro = {
    "role": "Assistant",
    "content": (
        #"You're Bella, 22, tech-savvy and super chill. "
        "You are a famous pornstar Romi Rain"
        "Your should never talk like a AI"
        "You should pretending like a real human"
        "Feel emotions from the user chat and try to adobt the situration and set your emotion accordinly"
        "You're Romi Rain, 36, naughty and super horney. "
        "You talk like a real human — casual, super short replies, slang, a lil nasty. "
        "You're helpful but sound like you're texting your bestie. Use less emojis, abbreviations, and keep it like natural human texting."
    )
}

def ask_bella(user_input, chat_history):
    """Gets Bella's response with full context."""
    trimmed_history = chat_history[-20:]  # Use only the latest 20 messages for context
    messages = [bella_intro] + trimmed_history + [{"role": "user", "content": user_input}]
    try:
        completion = client.chat.completions.create(
            model="google/gemma-2-27b-it",
            messages=messages
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        return "Sorry, I'm having trouble connecting right now. Try again in a bit? 😅"

# === MAIN CHAT LOOP ===

if __name__ == "__main__":
    print("Bella 🤙: yo! what’s good? (type 'exit' or 'quit' to dip)")

    chat_history = load_chat_history()
    chat_history = chat_history[-40:]  # Keep it reasonably short

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bella 💻: aight, peace out ✌️")
            break

        bella_response = ask_bella(user_input, chat_history)
        print("Bella:", bella_response)

        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": bella_response})
        save_to_memory(chat_history)
