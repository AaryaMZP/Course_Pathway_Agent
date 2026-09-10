from ibm_watsonx_orchestrate.agent_builder.tools import tool
import requests, os

BACKEND_URL = os.getenv("SKILLPILOT_BACKEND_URL", "http://host.docker.internal:3001")


@tool
def generate_roadmap(
    user_id: str,
    job_role: str,
    interest_area: str,
    current_skill_level: str,
    desired_weeks: int,
    hours_per_day: float,
) -> dict:
    """
    Generate a personalized week-by-week course roadmap using IBM Granite AI.
    Assesses whether the requested timeline is realistic; if not, suggests an adjusted plan.
    Persists the roadmap to the student's profile in Cloudant.

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
    resp = requests.post(
        f"{BACKEND_URL}/api/roadmap/generate",
        json={
            "userId": user_id,
            "jobRole": job_role,
            "interestArea": interest_area,
            "currentSkillLevel": current_skill_level,
            "desiredWeeks": desired_weeks,
            "hoursPerDay": hours_per_day,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()
