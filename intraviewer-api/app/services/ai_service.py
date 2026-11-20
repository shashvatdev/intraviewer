import json
import os
import re
from typing import Dict, Any
from groq import Groq
from app.core.config import settings

def _mock_analysis(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    exp_match = re.search(r'(\d+)\s*[-+to]*\s*(\d+)?\s*years?', text_lower)
    min_exp = int(exp_match.group(1)) if exp_match else 0
    max_exp = int(exp_match.group(2)) if exp_match and exp_match.group(2) else min_exp + 2
    
    role_level = "JUNIOR"
    if min_exp >= 3: role_level = "MID"
    if min_exp >= 6: role_level = "SENIOR"
    
    skills = []
    for s in ["python", "react", "fastapi", "sql", "aws", "docker", "node", "java"]:
        if s in text_lower: skills.append(s.title())
    
    if not skills:
        skills = ["Communication", "Problem Solving"]
        
    return {
        "required_skills": skills[:4],
        "good_to_have_skills": skills[4:],
        "hard_requirements": [f"{min_exp}+ years experience"],
        "preferred_requirements": ["Strong problem solving"],
        "minimum_experience": min_exp,
        "maximum_experience": max_exp,
        "education": ["B.Tech/BE or equivalent"],
        "role_level": role_level,
        "domain": "Engineering"
    }

def extract_jd_analysis(text: str) -> Dict[str, Any]:
    if not settings.GROQ_API_KEY:
        return _mock_analysis(text)
        
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    schema = {
        "required_skills": ["list of strings"],
        "good_to_have_skills": ["list of strings"],
        "minimum_experience_years": "int",
        "maximum_experience_years": "int",
        "education": ["list of strings"],
        "role_level": "JUNIOR, MID, or SENIOR",
        "domain": "string (e.g. BACKEND_ENGINEERING)",
        "hard_requirements": ["list of strings"],
        "preferred_requirements": ["list of strings"]
    }
    
    prompt = f"""
    Analyze the following Job Description and extract the key information in EXACTLY this JSON format:
    {json.dumps(schema, indent=2)}
    
    Job Description:
    {text}
    
    Return ONLY valid JSON.
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            response_format={"type": "json_object"},
            temperature=0.1
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # map keys to our model
        return {
            "required_skills": data.get("required_skills", []),
            "good_to_have_skills": data.get("good_to_have_skills", []),
            "hard_requirements": data.get("hard_requirements", []),
            "preferred_requirements": data.get("preferred_requirements", []),
            "minimum_experience": data.get("minimum_experience_years", 0),
            "maximum_experience": data.get("maximum_experience_years", 0),
            "education": data.get("education", []),
            "role_level": data.get("role_level", "JUNIOR"),
            "domain": data.get("domain", "Engineering")
        }
    except Exception as e:
        print("Groq API error:", e)
        return _mock_analysis(text)

def generate_blueprint(analysis: Dict[str, Any]) -> Dict[str, Any]:
    level = analysis.get("role_level", "JUNIOR")
    return {
        "persona_level": level,
        "estimated_duration": 30 if level == "SENIOR" else 20,
        "question_distribution": {
            "introduction": 2,
            "resume_deep_dive": 3,
            "technical": 4 if level == "SENIOR" else 3,
            "real_world": 2
        },
        "evaluation_weights": {
            "communication": 15,
            "technical": 45,
            "problem_solving": 40
        }
    }
