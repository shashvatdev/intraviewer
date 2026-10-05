import httpx
from app.core.config import settings

def transcribe_audio(file_path: str) -> str:
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
    
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}"
    }
    
    with open(file_path, "rb") as f:
        files = {
            "file": (file_path, f, "audio/mpeg")
        }
        data = {
            "model": "whisper-large-v3"
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            return response.json().get("text", "")
