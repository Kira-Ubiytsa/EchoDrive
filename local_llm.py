import requests, json
URL = "http://127.0.0.1:7860/v1/chat/completions"
SYSTEM_PROMPT = (
    "You are an over-the-top gaming hype coach. "
    "Reply with ONE short sentence (max 12 words)."
)

def generate_hype_line(context: str) -> str:
    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
        "temperature": 0.9,
        "max_tokens": 40,
    }
    try:
        r = requests.post(URL, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return "Let's go!"   # fallback
