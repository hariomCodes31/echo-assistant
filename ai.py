from groq import Groq
from dotenv import load_dotenv
import os
import json

# Load .env
load_dotenv()

# Groq Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_ai(prompt):
    model = "llama-3.3-70b-versatile"
    temperature = 0.7
    max_tokens = 1024

    try:
        import streamlit as st
        if "llm_model" in st.session_state:
            model = st.session_state.llm_model
        if "llm_temp" in st.session_state:
            temperature = st.session_state.llm_temp
        if "llm_max_tokens" in st.session_state:
            max_tokens = st.session_state.llm_max_tokens
    except Exception:
        pass

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

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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