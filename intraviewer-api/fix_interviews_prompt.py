import os

ROUTES_DIR = "app/api/routes"

with open(f"{ROUTES_DIR}/interviews.py", "r") as f:
    content = f.read()

old_json = """  "unclear_audio": boolean,
  "technical_score": int (0-100),
  "ai_cheating_probability": int (0-100)
}}"""

new_json = """  "unclear_audio": boolean,
  "technical_score": int (0-100),
  "ai_cheating_probability": int (0-100),
  "detailed_analysis": "string (Only when is_completed is true, write a detailed 4-5 sentence summary evaluating their technical skills, communication, and overall suitability)"
}}"""

content = content.replace(old_json, new_json)


old_eval = """        eval_details["stage"] = data.get("next_stage", eval_details.get("stage"))
        eval_details["ai_prob"] = data.get("ai_cheating_probability", 0)"""

new_eval = """        eval_details["stage"] = data.get("next_stage", eval_details.get("stage"))
        eval_details["ai_prob"] = data.get("ai_cheating_probability", 0)
        if data.get("detailed_analysis"):
            eval_details["detailed_analysis"] = data.get("detailed_analysis")"""

content = content.replace(old_eval, new_eval)

with open(f"{ROUTES_DIR}/interviews.py", "w") as f:
    f.write(content)

print("Updated prompt for detailed analysis")
