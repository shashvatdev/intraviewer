import os

with open("app/services/ai_service.py", "r") as f:
    content = f.read()

content = content.replace('model="llama3-70b-8192"', 'model="llama-3.1-70b-versatile"')

# We should also ensure it throws an error instead of returning mocked data if it fails, since user wants STRICTLY real data.
old_fallback_1 = """        print("Groq API Error:", e)
        # Fallback to simple parser if API fails
        return fallback_parse(raw_text)"""
        
new_fallback_1 = """        print("Groq API Error:", e)
        raise Exception(f"AI Parse failed: {str(e)}")"""
        
content = content.replace(old_fallback_1, new_fallback_1)

old_fallback_2 = """        print("Groq API Blueprint Error:", e)
        return fallback_blueprint(skills, role_level)"""
        
new_fallback_2 = """        print("Groq API Blueprint Error:", e)
        raise Exception(f"AI Blueprint failed: {str(e)}")"""
        
content = content.replace(old_fallback_2, new_fallback_2)

with open("app/services/ai_service.py", "w") as f:
    f.write(content)

print("Updated ai_service.py")
