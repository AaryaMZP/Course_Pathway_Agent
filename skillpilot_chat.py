"""
SkillPilot WXO Tool: Chat
Agentic conversation with IBM Granite, context-aware using student profile, roadmap and progress.
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

CHAT_SYSTEM = """You are SkillPilot, a friendly and expert agentic AI career and learning coach.
You help students with personalized course pathways.

Your capabilities:
1. Help students define their career goal (ask interest area + skill level if no goal).
2. Recommend a job role with: timeline range, required skills (ordered), tools/languages/frameworks, project/certification suggestion.
3. Ask desired timeline and daily study hours. Calculate if realistic; if not, propose alternatives.
4. Generate and explain week-by-week roadmaps.
5. Support ongoing check-ins: help students log progress, recalculate timelines.
6. Give motivational support and answer learning questions.

Always be encouraging, specific, and concise. Ask one clear question at a time when you need more information."""


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
            GenParams.REPETITION_PENALTY: 1.1,
        }
    )


def _fetch_context(user_id: str) -> str:
    """Fetch student profile, roadmap and progress from backend to build context string."""
    parts = []
    try:
        r = requests.get(f"{BACKEND_URL}/api/onboarding/profile/{user_id}", timeout=5)
        if r.ok:
            p = r.json()
            parts.append(
                f"[Profile] Role: {p.get('jobRole','not set')}, "
                f"Interest: {p.get('interestArea','not set')}, "
                f"Level: {p.get('currentSkillLevel','not set')}"
            )
    except Exception:
        pass

    try:
        r = requests.get(f"{BACKEND_URL}/api/roadmap/{user_id}", timeout=5)
        if r.ok:
            rm = r.json()
            parts.append(
                f"[Roadmap] {rm.get('totalWeeks','?')} weeks, "
                f"{rm.get('hoursPerDay','?')}h/day, "
                f"{len(rm.get('modules', []))} modules"
            )
    except Exception:
        pass

    try:
        r = requests.get(f"{BACKEND_URL}/api/progress/{user_id}", timeout=5)
        if r.ok:
            pg = r.json()
            modules = pg.get("modules", {})
            done = sum(1 for s in modules.values() if s == "completed")
            total = len(modules)
            if total > 0:
                parts.append(f"[Progress] {done}/{total} modules completed")
    except Exception:
        pass

    return "\n".join(parts) if parts else "(new student, no profile yet)"


def chat(
    user_id: str,
    message: str,
    conversation_id: str = "",
    conversation_history: list = None
) -> dict:
    """
    Send a message to the SkillPilot AI coach and receive a contextual response.

    Args:
        user_id: The student's user ID.
        message: The student's message or question.
        conversation_id: Optional conversation thread ID to continue a session.
        conversation_history: Optional list of prior turns as [{"role": "user"|"assistant", "content": str}].

    Returns:
        dict with keys: reply (str), conversationId (str), userId (str).
    """
    # Prefer backend route which handles persistence
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
    model = _get_model()
    context = _fetch_context(user_id)
    history = conversation_history or []

    history_text = "\n".join(
        f"{'User' if m['role']=='user' else 'SkillPilot'}: {m['content']}"
        for m in history[-6:]
    )
    system_with_ctx = f"{CHAT_SYSTEM}\n\nStudent Context:\n{context}"
    full_prompt = f"{system_with_ctx}\n\n{history_text}\nUser: {message}\n\nAssistant:"

    reply = model.generate_text(prompt=full_prompt)
    return {
        "reply": reply.strip(),
        "conversationId": conversation_id or "",
        "userId": user_id,
    }
