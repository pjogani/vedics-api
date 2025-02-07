from typing import Any, Dict
import logging
from datetime import datetime, date

from django.conf import settings
from django.contrib.auth import get_user_model

from assistant.assistant import get_assistant_response
from assistant.openai_utils import OpenAIAPI
from predictions.constants import PROMPT_MAPPING
from .astro_service import AstroService
from predictions.models import Prediction

logger = logging.getLogger(__name__)
User = get_user_model()


class ReadingService:
    """
    Combines birth chart data + prompts OpenAI for structured readings.
    Integrates logic from 'vedic-ai' reading_service.
    """

    def __init__(self):
        self.astro_service = AstroService()
        self.openai_api = OpenAIAPI()
        self.prompts = PROMPT_MAPPING


    def generate_reading(self, user: Any, reading_type: str = "today_reading") -> Dict[str, Any]:
        """
        Generate a reading by:
         1) Checking for user profile birth chart info
         2) Passing relevant prompt + chart info to OpenAI
         3) Storing the resulting content in the DB as a new Prediction
        """

        profile = getattr(user, "profile", None)
        if profile and profile.birth_chart:
            birth_chart = profile.birth_chart
        else:
            logger.warning(f"User {user.id} missing or incomplete birth data; using fallback chart.")
            birth_chart = {}

        # Determine the language for the response (from profile)
        user_language = "en"
        if profile and profile.preferred_language:
            user_language = profile.preferred_language

        # Construct the base prompt
        base_prompt = self.prompts.get(reading_type, self.prompts["today_reading"])
        content = (
            f"This is the user's birth chart:\n{birth_chart}\n\n"
            f"Provide a detailed reading:\n\n{base_prompt}\n\n"
            f"Response strictly should be in {user_language} language, the keys of the json should be in {user_language} language."
        )
        # TODO: Check if assistant needs to be used instead
        assistant_id = "asst_Hy3IbR2ctsWmirWqTlpidjqS"
        thread = self.openai_api.create_thread(
            metadata={"session_id": f"reading_{reading_type}"}
        )
        self.openai_api.add_message_to_thread(thread.id, content)
        response = get_assistant_response(thread.id, assistant_id)

        if not response:
          response = self.openai_api.generate_extracted_info(
              prompt="You are a helpful Vedic astrology assistant.",
              content=content
          )
          if response["status"] == "SUCCESS":
              response = response["response"]

        if not isinstance(response, dict):
            response = response or {}
            # If not a structured JSON, wrap in dict
            response = {"raw": str(response)}

        # Store the new reading
        pred_obj = Prediction.objects.create(
            user=user,
            prediction_type=reading_type,
            content=response
        )

        return pred_obj
