"""
SkillPilot WXO Tool: Progress Tracker
Logs module completion and recalculates the remaining roadmap timeline using IBM Granite.
"""
import os
import json
import re
import requests
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "ao9qLDOFvi_lV13f0PzSQfPkqVp40v7Y_JlMGCQVJX_5")
WATSONX_URL     = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT = os.getenv("WATSONX_PROJECT_ID", "2c02dcad-09a1-4ba9-9b3d-d29f964ee048")
MODEL_ID        = os.getenv("WATSONX_MODEL_ID", "ibm/granite-4-h-small")

BACKEND_URL = os.getenv("SKILLPILOT_BACKEND_URL", "http://localhost:3001")

RECALC_SYSTEM = """You are SkillPilot, an expert learning coach.
Given a user's roadmap and their completed module IDs, recalculate the remaining schedule.

Output ONLY valid JSON:
{
  "completedModules": [string],
  "remainingModules": [{"id": string, "title": string, "targetWeek": number, "hoursEstimate": number}],
  "newEstimatedCompletionWeek": number,
  "motivationalMessage": string
}"""


def _get_model():
    creds = Credentials(api_key=WATSONX_API_KEY, url=WATSONX_URL)
    return ModelInference(
        model_id=MODEL_ID,
        project_id=WATSONX_PROJECT,
        credentials=creds,
        params={
            GenParams.MAX_NEW_TOKENS: 800,
            GenParams.DECODING_METHOD: "greedy",
            GenParams.STOP_SEQUENCES: ["User:"],
        }
    )


def update_progress(
    user_id: str,
    module_id: str,
    status: str
) -> dict:
    """
    Update the completion status of a roadmap module and recalculate the remaining timeline.

    Args:
        user_id: The student's user ID.
        module_id: The module ID to update (e.g. 'm1', 'm3').
        status: One of 'completed', 'in_progress', 'not_started'.

    Returns:
        dict with updated progress and recalculated remaining roadmap.
    """
    # Post to backend — it handles Cloudant persistence and recalc
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

    # Fallback: call Granite directly if backend is unreachable
    model = _get_model()
    prompt = (
        f"{RECALC_SYSTEM}\n\n"
        f"User: Module '{module_id}' is now '{status}' for user '{user_id}'. "
        f"Please update progress and provide a motivational message.\n\nAssistant:"
    )
    raw = model.generate_text(prompt=prompt)
    try:
        return json.loads(raw)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", raw)
        return json.loads(match.group(0)) if match else {"status": status, "moduleId": module_id}


def get_progress(user_id: str) -> dict:
    """
    Retrieve current progress for a student.

    Args:
        user_id: The student's user ID.

    Returns:
        dict with modules dict (moduleId -> status) and logs list.
    """
    try:
        resp = requests.get(f"{BACKEND_URL}/api/progress/{user_id}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {"userId": user_id, "modules": {}, "logs": []}
