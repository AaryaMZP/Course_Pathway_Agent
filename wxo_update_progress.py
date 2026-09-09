"""
SkillPilot WXO Tool: Update Progress
Logs a module status change and recalculates the remaining roadmap timeline.
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

RECALC_SYSTEM = (
    "You are SkillPilot, an expert learning coach. "
    "Given a user's roadmap modules and completed module IDs, recalculate the remaining schedule. "
    "Output ONLY valid JSON: "
    '{"completedModules": [string], '
    '"remainingModules": [{"id": string, "title": string, "targetWeek": number, "hoursEstimate": number}], '
    '"newEstimatedCompletionWeek": number, '
    '"motivationalMessage": string}'
)


@tool
def update_progress(
    user_id: str,
    module_id: str,
    status: str
) -> dict:
    """
    Record a student's progress on a specific roadmap module, then recalculate
    the remaining learning timeline using IBM Granite AI.

    Args:
        user_id: The student's user ID.
        module_id: The module ID to update (e.g. 'm1', 'm3').
        status: The new status: 'completed', 'in_progress', or 'not_started'.

    Returns:
        dict with success flag, updated progress map, and AI-recalculated remaining schedule.
    """
    # Primary: delegate to backend (handles Cloudant + Granite recalc)
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/progress/update",
            json={"userId": user_id, "moduleId": module_id, "status": status},
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException:
        pass

    # Fallback: call Granite directly when backend is unreachable
    creds = Credentials(api_key=WATSONX_API_KEY, url=WATSONX_URL)
    model = ModelInference(
        model_id=MODEL_ID,
        project_id=WATSONX_PROJECT,
        credentials=creds,
        params={
            GenParams.MAX_NEW_TOKENS: 600,
            GenParams.DECODING_METHOD: "greedy",
            GenParams.STOP_SEQUENCES: ["User:"],
        }
    )
    prompt = (
        f"{RECALC_SYSTEM}\n\n"
        f"User: Module '{module_id}' is now '{status}' for student '{user_id}'. "
        f"Provide recalculated schedule and a motivational message.\n\nAssistant:"
    )
    raw = model.generate_text(prompt=prompt)
    try:
        return json.loads(raw)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", raw)
        return json.loads(match.group(0)) if match else {
            "success": True, "moduleId": module_id, "status": status
        }


@tool
def get_progress(user_id: str) -> dict:
    """
    Retrieve the current learning progress for a student.

    Args:
        user_id: The student's user ID.

    Returns:
        dict with modules (moduleId -> status), logs, and userId.
    """
    try:
        resp = requests.get(f"{BACKEND_URL}/api/progress/{user_id}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {"userId": user_id, "modules": {}, "logs": []}
