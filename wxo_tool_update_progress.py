from ibm_watsonx_orchestrate.agent_builder.tools import tool
import requests, os

BACKEND_URL = os.getenv("SKILLPILOT_BACKEND_URL", "http://host.docker.internal:3001")


@tool
def update_progress(user_id: str, module_id: str, status: str) -> dict:
    """
    Record a student's progress on a specific roadmap module, then recalculate
    the remaining learning timeline using IBM Granite AI.

    Args:
        user_id: The student's user ID.
        module_id: The module ID to update (e.g. 'm1', 'm3').
        status: The new status — one of 'completed', 'in_progress', or 'not_started'.

    Returns:
        dict with success flag, updated progress map, and AI-recalculated remaining schedule.
    """
    resp = requests.post(
        f"{BACKEND_URL}/api/progress/update",
        json={"userId": user_id, "moduleId": module_id, "status": status},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
