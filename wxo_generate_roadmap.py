"""
SkillPilot WXO Tool: Generate Roadmap
Generates a personalized week-by-week learning roadmap using IBM Granite.
"""
import os
import json
import re
import requests
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "ao9qLDOFvi_lV13f0PzSQfPkqVp40v7Y_JlMGCQVJX_5")
WATSONX_URL     = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT = os.getenv("WATSONX_PROJECT_ID", "2c02dcad-09a1-4ba9-9b3d-d29f964ee048")
MODEL_ID        = os.getenv("WATSONX_MODEL_ID", "ibm/granite-4-h-small")
BACKEND_URL     = os.getenv("SKILLPILOT_BACKEND_URL", "http://localhost:3001")

ROADMAP_SYSTEM = """You are SkillPilot, an expert learning roadmap designer.
Given a job role, interest area, current skill level, desired timeline (weeks), and daily study hours,
produce a detailed week-by-week learning roadmap.

Output ONLY valid JSON:
{
  "jobRole": string,
  "totalWeeks": number,
  "hoursPerDay": number,
  "isRealistic": boolean,
  "adjustmentNote": string or null,
  "requiredSkills": [string],
  "toolsAndTech": [string],
  "certificationSuggestion": string,
  "projectSuggestion": string,
  "modules": [
    {
      "id": string,
      "title": string,
      "description": string,
      "skills": [string],
      "hoursEstimate": number,
      "targetWeek": number,
      "prerequisites": [string]
    }
  ]
}
Ensure modules are ordered with prerequisites respected. Be realistic about hours."""


@tool
def generate_roadmap(
    user_id: str,
    job_role: str,
    interest_area: str,
    current_skill_level: str,
    desired_weeks: int,
    hours_per_day: float
) -> dict:
    """
    Generate a personalized week-by-week course roadmap using IBM Granite AI.
    Assess whether the requested timeline is realistic and if not, suggest an adjusted plan.
    Persists the roadmap to the student's profile.

    Args:
        user_id: The student's user ID for persistence.
        job_role: Target job role (e.g. 'Frontend Developer', 'Data Scientist').
        interest_area: Interest area (e.g. 'Frontend', 'Backend', 'Cybersecurity', 'UI/UX').
        current_skill_level: One of 'beginner', 'intermediate', 'advanced'.
        desired_weeks: Number of weeks the student wants to complete the roadmap.
        hours_per_day: How many hours per day the student can study.

    Returns:
        Full roadmap dict with modules, skills, tools, certification and project suggestions.
    """
    creds = Credentials(api_key=WATSONX_API_KEY, url=WATSONX_URL)
    model = ModelInference(
        model_id=MODEL_ID,
        project_id=WATSONX_PROJECT,
        credentials=creds,
        params={
            GenParams.MAX_NEW_TOKENS: 2400,
            GenParams.DECODING_METHOD: "greedy",
            GenParams.STOP_SEQUENCES: ["User:"],
        }
    )

    user_prompt = (
        f"Generate a course roadmap for:\n"
        f"- Job Role: {job_role}\n"
        f"- Interest Area: {interest_area}\n"
        f"- Current Skill Level: {current_skill_level}\n"
        f"- Desired Timeline: {desired_weeks} weeks\n"
        f"- Daily Study Hours: {hours_per_day} hours/day"
    )
    full_prompt = f"{ROADMAP_SYSTEM}\n\nUser: {user_prompt}\n\nAssistant:"
    raw = model.generate_text(prompt=full_prompt)

    try:
        roadmap = json.loads(raw)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", raw)
        roadmap = json.loads(match.group(0)) if match else {"error": "parse_failed", "raw": raw}

    # Persist to backend
    if user_id:
        try:
            requests.post(
                f"{BACKEND_URL}/api/roadmap/generate",
                json={
                    "userId": user_id,
                    "jobRole": job_role,
                    "interestArea": interest_area,
                    "currentSkillLevel": current_skill_level,
                    "desiredWeeks": desired_weeks,
                    "hoursPerDay": hours_per_day,
                },
                timeout=30
            )
        except Exception:
            pass

    return roadmap
