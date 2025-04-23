"""
local_llm.py – POST to text-generation-webui (run with:  python server.py --listen --api)
"""

import requests, json, logging

URL = "http://127.0.0.1:5000/v1/chat/completions"   # port 5000 = OpenAI-style endpoint
SYSTEM = ("You are an over-the-top gaming hype coach. "
          "Reply with ONE short sentence (max 12 words).")

def generate_hype_line(context: str) -> str:
    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": context}
        ],
        "temperature": 0.9,
        "max_tokens": 40,
    }
    try:
        r = requests.post(URL, json=payload, timeout=30)
        r.raise_for_status()
        line = r.json()["choices"][0]["message"]["content"].strip()
        logging.info("LLM: %s", line)
        return line
    except Exception as e:
        logging.error("LLM error: %s", e)
        return "Let's go!"   # safe fallback
