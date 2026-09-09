from ibm_watsonx_orchestrate.agent_builder.tools import tool
import requests, os

BACKEND_URL = os.getenv("SKILLPILOT_BACKEND_URL", "http://host.docker.internal:3001")


@tool
def get_progress(user_id: str) -> dict:
    """
    Retrieve the current learning progress for a student, including completed modules and logs.

    Args:
        user_id: The student's user ID.

    Returns:
        dict with modules (moduleId -> status), logs list, and userId.
    """
    resp = requests.get(f"{BACKEND_URL}/api/progress/{user_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()
