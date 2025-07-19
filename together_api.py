import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

def generate_flashcards_togetherai(text, num_flashcards=5):
    prompt = f"""
Generate exactly {num_flashcards} flashcards from the following text.

Each flashcard should follow this format:

Q: <question>
A: <answer>

Text:
\"\"\"{text}\"\"\"
"""

    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "messages": [
            {"role": "system", "content": "You are an AI that generates study flashcards from text."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 700
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ Error from Together AI: {response.status_code}\n\n{response.text}"
