import logging

from assistant.assistant import get_assistant_response

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

    def chat(self, session_id, user_input):
        """
        Posts a user message to a conversation and gets an AI reply.
        If conversation_id is None or invalid for this user, creates a new conversation.
        Returns a dict with "reply" and "conversation_id".
        """

        # Retrieve or create conversation
        conversation = None
        if session_id:
            conversation = Conversation.objects.filter(session_id=session_id, user=self.user).first()

        if not conversation:
            assistant_id = "asst_Quv8mSsNKh3wfx8GUJkX7yqx"
            conversation = Conversation.objects.create(
                user=self.user,
                assistant_id=assistant_id,
                session_id=session_id,
            )

        if conversation and not conversation.thread_id:
            thread = self.openai_api.create_thread(metadata={"conversation_id": str(conversation.id)})
            conversation.thread_id = thread.id
            conversation.save()
            user_profile = self.user.profile
            user_info = f"This is the user's information: Birth Date: {user_profile.date_of_birth}, Birth Time: {user_profile.time_of_birth} UTC, Place of Birth: {user_profile.place_of_birth}, Latitude: {user_profile.latitude}, Longitude: {user_profile.longitude}. The responses in this thread should be strictly in {user_profile.preferred_language} language."
            self.openai_api.add_message_to_thread(conversation.thread_id, user_info)
            user_info = f"This is the user's birth chart: {user_profile.birth_chart}"
            self.openai_api.add_message_to_thread(conversation.thread_id, user_info)

        # Store user message
        Message.objects.create(
            conversation=conversation,
            role="user",
            content=user_input
        )
        self.openai_api.add_message_to_thread(conversation.thread_id, user_input)
        response = self.generate_reply(conversation.thread_id, conversation.assistant_id)
        assistant_reply = str(response)

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

    def generate_reply(self, thread_id, assistant_id) -> dict:
        return get_assistant_response(thread_id, assistant_id)
