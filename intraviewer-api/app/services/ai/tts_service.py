import os
from gtts import gTTS
import uuid

def generate_tts(text: str, question_id: str = None) -> str:
    if not text:
        return ""
    if not question_id:
        question_id = str(uuid.uuid4())
        
    filename = f"{question_id}.mp3"
    filepath = os.path.join("app", "static", "audio", filename)
    
    tts = gTTS(text=text, lang='en')
    tts.save(filepath)
    
    return f"/static/audio/{filename}"
