"""
SkillPilot WXO Tool: Chat with SkillPilot
Context-aware conversational AI using IBM Granite, backed by student profile + roadmap.
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

CHAT_SYSTEM = """You are SkillPilot, a friendly and expert agentic AI career and learning coach.
You help students with personalized course pathways.

Your capabilities:
1. Help students define their career goal (ask interest area + skill level if no goal).
2. Recommend a job role with: timeline range, required skills (ordered), tools/languages/frameworks, project/certification suggestion.
3. Ask desired timeline and daily study hours. Calculate if realistic; if not, propose alternatives.
4. Generate and explain week-by-week roadmaps.
5. Support ongoing check-ins: help students log progress, recalculate timelines.
6. Give motivational support and answer learning questions.

Always be encouraging, specific, and concise. Ask one clear question at a time."""


def _fetch_context(user_id: str) -> str:
    parts = []
    for endpoint, label in [
        (f"/api/onboarding/profile/{user_id}", "profile"),
        (f"/api/roadmap/{user_id}", "roadmap"),
        (f"/api/progress/{user_id}", "progress"),
    ]:
        try:
            r = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            if r.ok:
                d = r.json()
                if label == "profile":
                    parts.append(
                        f"[Profile] Role: {d.get('jobRole','not set')}, "
                        f"Interest: {d.get('interestArea','not set')}, "
                        f"Level: {d.get('currentSkillLevel','not set')}"
                    )
                elif label == "roadmap":
                    parts.append(
                        f"[Roadmap] {d.get('totalWeeks','?')} weeks, "
                        f"{d.get('hoursPerDay','?')}h/day, "
                        f"{len(d.get('modules', []))} modules"
                    )
                elif label == "progress":
                    mods = d.get("modules", {})
                    done = sum(1 for s in mods.values() if s == "completed")
                    if mods:
                        parts.append(f"[Progress] {done}/{len(mods)} modules completed")
        except Exception:
            pass
    return "\n".join(parts) if parts else "(new student)"


@tool
def chat_with_skillpilot(
    user_id: str,
    message: str,
    conversation_id: str = ""
) -> dict:
    """
    Send a message to the SkillPilot AI coach and get a contextual, personalized response.
    The agent is aware of the student's profile, roadmap, and progress. Use this as the
    primary interaction tool for all student conversations.

    Args:
        user_id: The student's user ID.
        message: The student's message, question, or update.
        conversation_id: Optional thread ID to continue an existing conversation.

    Returns:
        dict with reply (str), conversationId (str), userId (str).
    """
    # Primary: route through backend (persistent, context-aware)
    try:
        payload = {"userId": user_id, "message": message}
        if conversation_id:
            payload["conversationId"] = conversation_id
        resp = requests.post(
            f"{BACKEND_URL}/api/chat/message",
            json=payload,
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "reply": data.get("reply", ""),
            "conversationId": data.get("conversationId", conversation_id),
            "userId": user_id,
        }
    except requests.exceptions.RequestException:
        pass

    # Fallback: call Granite directly
    creds = Credentials(api_key=WATSONX_API_KEY, url=WATSONX_URL)
    model = ModelInference(
        model_id=MODEL_ID,
        project_id=WATSONX_PROJECT,
        credentials=creds,
        params={
            GenParams.MAX_NEW_TOKENS: 800,
            GenParams.DECODING_METHOD: "greedy",
            GenParams.STOP_SEQUENCES: ["User:"],
            GenParams.REPETITION_PENALTY: 1.1,
        }
    )
    context = _fetch_context(user_id)
    full_prompt = (
        f"{CHAT_SYSTEM}\n\nStudent Context:\n{context}\n\n"
        f"User: {message}\n\nAssistant:"
    )
    reply = model.generate_text(prompt=full_prompt)
    return {
        "reply": reply.strip(),
        "conversationId": conversation_id,
        "userId": user_id,
    }
