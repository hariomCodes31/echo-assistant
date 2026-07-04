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

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=1024,
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