import logging
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import ConversationMessage
from .openai_utils import OpenAIAPI

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages a user's conversation by storing messages in the DB and
    retrieving AI responses from OpenAI. Integrates logic from the 'vedic-ai'
    approach, adapted for Django.
    """

    def __init__(self, user):
        self.user = user
        self.openai_api = OpenAIAPI()

    def chat(self, session_id: str, user_input: str) -> dict:
        """
        Main entry point to handle a chat message.
          1) Store the user's message in DB
          2) Build conversation context from past messages
          3) Call LLM via OpenAI to get an assistant reply
          4) Store the assistant reply in DB
          5) Return the reply
        """

        # 1) Store user message
        user_msg = ConversationMessage.objects.create(
            user=self.user,
            session_id=session_id,
            role="user",
            content=user_input,
        )

        # 2) Build conversation context
        # We collect recent messages from this session. You can set a max length if needed.
        all_msgs = ConversationMessage.objects.filter(
            user=self.user,
            session_id=session_id
        ).order_by("created_at")

        conversation_history = []
        for msg in all_msgs:
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # 3) Call the LLM
        reply = self.openai_api.chat_completion(conversation_history)

        # 4) Store assistant's reply
        if isinstance(reply, dict) and "error" in reply:
            # If there's an error, just store something minimal
            assistant_reply = f"[Assistant Error]: {reply.get('detail')}"
        elif isinstance(reply, dict):
            # If it's a parsed JSON, let's store as a string
            assistant_reply = str(reply)
        else:
            assistant_reply = str(reply)

        ConversationMessage.objects.create(
            user=self.user,
            session_id=session_id,
            role="assistant",
            content=assistant_reply,
        )

        # 5) Return
        return {"reply": assistant_reply}
