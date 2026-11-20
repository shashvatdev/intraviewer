import os

ROUTES_DIR = "app/api/routes"

with open(f"{ROUTES_DIR}/interviews.py", "r") as f:
    content = f.read()

# Add elevenlabs to the config checking logic
if "import requests" not in content:
    content = "import requests\n" + content

old_tts = """def get_tts_sync(text: str) -> str:
    \"\"\"Generates TTS using edge-tts synchronously and returns base64 audio.\"\"\"
    async def _generate():
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
        tmp_path = tempfile.mktemp(suffix=".mp3")
        await communicate.save(tmp_path)
        with open(tmp_path, "rb") as f:
            data = f.read()
        os.remove(tmp_path)
        return base64.b64encode(data).decode("utf-8")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(_generate())
    loop.close()
    return result"""

new_tts = """def get_tts_sync(text: str) -> str:
    \"\"\"Generates TTS using ElevenLabs if API key is present, else falls back to edge-tts.\"\"\"
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    if elevenlabs_key:
        try:
            # Using Rachel (friendly female voice) or any standard voice ID
            voice_id = "21m00Tcm4TlvDq8ikWAM" 
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": elevenlabs_key
            }
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode("utf-8")
            else:
                print("ElevenLabs error:", response.text)
        except Exception as e:
            print("ElevenLabs exception:", e)
            
    # Fallback to Edge-TTS
    async def _generate():
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
        tmp_path = tempfile.mktemp(suffix=".mp3")
        await communicate.save(tmp_path)
        with open(tmp_path, "rb") as f:
            data = f.read()
        os.remove(tmp_path)
        return base64.b64encode(data).decode("utf-8")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(_generate())
    loop.close()
    return result"""

content = content.replace(old_tts, new_tts)

with open(f"{ROUTES_DIR}/interviews.py", "w") as f:
    f.write(content)

print("Updated backend for ElevenLabs TTS")
