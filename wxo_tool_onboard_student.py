from ibm_watsonx_orchestrate.agent_builder.tools import tool
import requests, os, json, re

BACKEND_URL = os.getenv("SKILLPILOT_BACKEND_URL", "http://host.docker.internal:3001")


@tool
def onboard_student(user_message: str, user_id: str = "") -> dict:
    """
    Start or continue student onboarding. Identifies the student's career goal
    using IBM Granite AI via the SkillPilot backend. Returns structured profile info.

    Args:
        user_message: The student's first message or response about their career interest.
        user_id: Optional student identifier for session persistence.

    Returns:
        dict with status, message, jobRole, interestArea, currentSkillLevel, userId.
    """
    resp = requests.post(
        f"{BACKEND_URL}/api/onboarding/start",
        json={"userId": user_id, "message": user_message},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
