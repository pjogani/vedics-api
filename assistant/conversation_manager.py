import logging
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .openai_utils import OpenAIAPI

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages a user's conversation flow, storing messages in the DB and
    retrieving AI responses from OpenAI.
    """

    def __init__(self, user):
        self.user = user
        self.openai_api = OpenAIAPI()

        # Attempt to read user's preferred language from their profile
        self.language = "en"
        if hasattr(user, "profile") and user.profile.preferred_language:
            self.language = user.profile.preferred_language

    def chat(self, conversation_id, user_input):
        """
        Posts a user message to a conversation and gets an AI reply.
        If conversation_id is None or invalid for this user, creates a new conversation.
        Returns a dict with "reply" and "conversation_id".
        """

        # Retrieve or create conversation
        conversation = None
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=self.user)
            except Conversation.DoesNotExist:
                logger.warning(
                    f"Conversation {conversation_id} not found or not owned by user {self.user}. "
                    f"Creating a new conversation instead."
                )

        if not conversation:
            conversation = Conversation.objects.create(user=self.user)

        # Store user message
        Message.objects.create(
            conversation=conversation,
            role="user",
            content=user_input
        )

        # Build the conversation context
        past_msgs = conversation.messages.order_by("created_at")
        conversation_history = [{"role": m.role, "content": m.content} for m in past_msgs]

        # Insert a system message at the start about responding in the user's language
        system_prompt = (
            f"You are a helpful Vedic astrology assistant. "
            f"Please respond in {self.language}."
        )
        conversation_history.insert(0, {"role": "system", "content": system_prompt})

        # Call OpenAI
        reply = self.openai_api.chat_completion(conversation_history)

        # Determine reply text (string or error dict)
        if isinstance(reply, dict) and "error" in reply:
            assistant_reply = f"[Assistant Error]: {reply.get('detail')}"
        elif isinstance(reply, dict):
            assistant_reply = str(reply)
        else:
            assistant_reply = str(reply)

        # Store assistant's reply
        Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=assistant_reply
        )

        return {
            "reply": assistant_reply,
            "conversation_id": conversation.id
        }
