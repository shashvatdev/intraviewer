import os

ROUTES_DIR = "app/api/routes"

with open(f"{ROUTES_DIR}/interviews.py", "r") as f:
    content = f.read()

# Add gTTS logic to send_message
if "import base64" not in content:
    content = "import base64\nfrom io import BytesIO\nfrom gtts import gTTS\n" + content

old_return = """        return ok("Message processed", {
            "response": ai_response,
            "is_completed": is_completed
        })"""

new_return = """        
        audio_base64 = ""
        try:
            tts = gTTS(text=ai_response, lang='en', tld='co.uk') # Use UK accent for professional AI feel
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            audio_base64 = base64.b64encode(fp.read()).decode("utf-8")
        except Exception as e:
            print("gTTS error:", e)
            
        return ok("Message processed", {
            "response": ai_response,
            "is_completed": is_completed,
            "audio_base64": audio_base64
        })"""

content = content.replace(old_return, new_return)

with open(f"{ROUTES_DIR}/interviews.py", "w") as f:
    f.write(content)

print("Updated backend to send gTTS audio")
