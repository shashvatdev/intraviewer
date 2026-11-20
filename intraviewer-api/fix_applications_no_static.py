import os

ROUTES_DIR = "app/api/routes"

with open(f"{ROUTES_DIR}/applications.py", "r") as f:
    content = f.read()

# Remove static fallback
old_fallback = """    if not settings.GROQ_API_KEY:
        score = 75
        if "python" in resume_text.lower() and "python" in [s.lower() for s in required_skills]:
            score += 10
        return {
            "match_score": min(score, 100),
            "reasoning": "Fallback analysis: The candidate possesses some of the core skills."
        }"""
        
new_fallback = """    if not settings.GROQ_API_KEY:
        raise Exception("GROQ_API_KEY is not set.")"""
        
content = content.replace(old_fallback, new_fallback)

# Remove the try-except fallback return
old_except = """    except Exception as e:
        print("AI Match Error:", e)
        return {"match_score": 60, "reasoning": "Failed to analyze fully due to error."}"""
        
new_except = """    except Exception as e:
        print("AI Match Error:", e)
        raise ApiError(500, f"AI Analysis failed: {str(e)}")"""
        
content = content.replace(old_except, new_except)

# Update model
content = content.replace('model="llama3-8b-8192"', 'model="llama-3.1-8b-instant"')

with open(f"{ROUTES_DIR}/applications.py", "w") as f:
    f.write(content)

print("Updated applications.py")
