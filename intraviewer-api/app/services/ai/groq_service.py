import httpx
from app.core.config import settings

def call_groq_json(prompt: str, model: str = "llama-3.1-70b-versatile") -> dict:
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Output exactly in JSON format."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        import json
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
