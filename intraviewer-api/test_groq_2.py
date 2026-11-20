import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

try:
    res = client.chat.completions.create(
        messages=[{"role": "user", "content": "Return exactly this JSON: {\"status\": \"ok\"}"}],
        model="openai/gpt-oss-120b",
        response_format={"type": "json_object"}
    )
    print("SUCCESS:", res.choices[0].message.content)
except Exception as e:
    print("ERROR:", e)
