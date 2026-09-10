"""
SkillPilot WXO Tool: Onboard Student
Wraps skillpilot_onboarding for watsonx Orchestrate with the @tool decorator.
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

SYSTEM_PROMPT = (
    "You are SkillPilot, an expert career and learning coach. "
    "Your task is to help a student define their career goal. "
    "If they already have a goal, confirm and extract: jobRole, interestArea, currentSkillLevel. "
    "If they have no goal, ask their interest area and current skill level, then recommend a specific job role. "
    "Output ONLY valid JSON with keys: status ('needs_goal'|'goal_set'), message (string), "
    "jobRole (string or null), interestArea (string or null), "
    "currentSkillLevel ('beginner'|'intermediate'|'advanced'|null)."
)


@tool
def onboard_student(user_message: str, user_id: str = "") -> dict:
    """
    Start or continue student onboarding. Identifies the student's career goal
    using IBM Granite AI. Returns structured profile info.

    Args:
        user_message: The student's first message or response about their career interest.
        user_id: Optional student identifier for session persistence.

    Returns:
        dict with status, message, jobRole, interestArea, currentSkillLevel, userId.
    """
    creds = Credentials(api_key=WATSONX_API_KEY, url=WATSONX_URL)
    model = ModelInference(
        model_id=MODEL_ID,
        project_id=WATSONX_PROJECT,
        credentials=creds,
        params={
            GenParams.MAX_NEW_TOKENS: 400,
            GenParams.DECODING_METHOD: "greedy",
            GenParams.STOP_SEQUENCES: ["User:"],
        }
    )

    prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}\n\nAssistant:"
    raw = model.generate_text(prompt=prompt)

    try:
        parsed = json.loads(raw)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", raw)
        parsed = json.loads(match.group(0)) if match else {"status": "needs_goal", "message": raw}

    if user_id:
        try:
            requests.post(
                f"{BACKEND_URL}/api/onboarding/start",
                json={"userId": user_id, "message": user_message},
                timeout=10
            )
        except Exception:
            pass

    parsed["userId"] = user_id
    return parsed
