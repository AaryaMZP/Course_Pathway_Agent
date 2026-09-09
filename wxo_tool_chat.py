from ibm_watsonx_orchestrate.agent_builder.tools import tool
import requests, os

BACKEND_URL = os.getenv("SKILLPILOT_BACKEND_URL", "http://host.docker.internal:3001")


@tool
def chat_with_skillpilot(user_id: str, message: str, conversation_id: str = "") -> dict:
    """
    Send a message to the SkillPilot AI coach and get a contextual, personalized response.
    The agent is aware of the student's profile, roadmap, and progress stored in Cloudant.
    Use this as the primary interaction tool for all student conversations.

    Args:
        user_id: The student's user ID.
        message: The student's message, question, or progress update.
        conversation_id: Optional thread ID to continue an existing conversation.

    Returns:
        dict with reply (string), conversationId (string), userId (string).
    """
    payload = {"userId": user_id, "message": message}
    if conversation_id:
        payload["conversationId"] = conversation_id
    resp = requests.post(
        f"{BACKEND_URL}/api/chat/message",
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()
