# backend/llm.py
import os
from dotenv import load_dotenv

load_dotenv()

# NOTE: your project used AzureOpenAI earlier. keep same client initialization
# If you already have a client variable, keep it — here is a compatible pattern:
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-nano")
SYSTEM_PROMPT = os.getenv("AZURE_SYSTEM_PROMPT", "You are a helpful voice assistant that replies concisely and politely.")

# simple in-memory memory store: { session_id: [ {"role": "user"/"assistant", "content": "..."} ] }
SESSION_MEMORY = {}
MAX_MEMORY_TURNS = 6  # keep last N turns (user+assistant counts as one turn if you like)


def append_memory(session_id: str, role: str, content: str):
    if not session_id:
        return
    SESSION_MEMORY.setdefault(session_id, []).append({"role": role, "content": content})
    # trim memory
    if len(SESSION_MEMORY[session_id]) > MAX_MEMORY_TURNS * 2:
        SESSION_MEMORY[session_id] = SESSION_MEMORY[session_id][-MAX_MEMORY_TURNS * 2 :]


def get_memory_messages(session_id: str):
    if not session_id:
        return []
    return SESSION_MEMORY.get(session_id, [])


def ask_llm(user_text: str, session_id: str = None, temperature: float = 0.2) -> str:
    """
    Sends user_text + remembered conversation to Azure OpenAI and returns assistant text.
    Also appends user and assistant messages to session memory if session_id is provided.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # attach memory (if any)
    messages += get_memory_messages(session_id)

    # append current user turn
    messages.append({"role": "user", "content": user_text})

    # call Azure OpenAI chat completion (keeps your previous usage pattern)
    resp = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=messages,
        temperature=temperature,
    )

    # extract assistant text (adjust according to your client response shape)
    assistant_text = resp.choices[0].message.content

    # store in memory
    append_memory(session_id, "user", user_text)
    append_memory(session_id, "assistant", assistant_text)

    return assistant_text
