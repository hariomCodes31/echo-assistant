from groq import Groq
from dotenv import load_dotenv
import os
import json

# Load .env
_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=_ENV_PATH)

# Groq Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

DEFAULT_MODEL = "qwen/qwen3.8-27b"


def ask_ai(prompt):
    model = DEFAULT_MODEL
    temperature = 0.7
    max_tokens = 1024

    try:
        import streamlit as st
        if "llm_model" in st.session_state and st.session_state.llm_model:
            # If the session model is the old deprecated llama model, migrate it to the working model
            if "llama-3.3" in str(st.session_state.llm_model):
                st.session_state.llm_model = DEFAULT_MODEL
            model = st.session_state.llm_model
        if "llm_temp" in st.session_state:
            temperature = st.session_state.llm_temp
        if "llm_max_tokens" in st.session_state:
            max_tokens = st.session_state.llm_max_tokens
    except Exception:
        pass

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback to default model if a custom model fails
        if model != DEFAULT_MODEL:
            try:
                response = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
            except Exception:
                pass
        return f"ECHO AI Error: {e}"


def choose_action(prompt):
    system_prompt = """
You are an AI agent.

Choose ONE tool.

Available tools:

1. browser
2. weather
3. sports
4. music
5. desktop
6. chat

Return ONLY valid JSON.

Example:

{
    "tool":"browser",
    "action":"open_youtube",
    "query":""
}

If normal conversation:

{
    "tool":"chat"
}
"""

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        return json.loads(
            response.choices[0].message.content
        )
    except Exception:
        return {"tool": "chat"}