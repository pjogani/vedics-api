from typing import Any, Dict
import logging

from django.conf import settings

from assistant.openai_utils import OpenAIAPI
from .astro_service import AstroService
from predictions.models import UserReading
from django.contrib.auth import get_user_model

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

        # Define sample prompts or reading types
        self.prompts = {
            "core_personality_and_life_path": """
You are a Vedic astrology expert. Analyze the provided birth chart to describe:
1. Core personality traits and life path
2. Social perception and past life influences
Return JSON only with this shape:
{
  "core_personality_and_life_path": {
    "traits": [...],
    "strengths": [...],
    "weaknesses": [...],
    "social_perception": "...",
    "past_life_influence": "..."
  }
}""",
            "career_success_and_wealth": """
You are a Vedic astrology expert. Analyze the provided birth chart for career insights:
1. Career success and wealth potential
2. Foreign opportunities
3. Business vs employment
Return JSON with shape:
{
  "career_success_and_wealth": {
    "ideal_professions": [...],
    "financial_growth": {
      "trend": "...",
      "wealth_accumulation": "..."
    },
    "foreign_opportunities": "...",
    "career_transformation": {
      "expected_age_range": "...",
      "prediction": "..."
    },
    "business_vs_job": "..."
  }
}""",
            "relationships_love_and_marriage": """
You are a Vedic astrology expert. Analyze the provided birth chart for relationship insights:
Return JSON with shape:
{
  "relationships_love_and_marriage": {
    "traits_in_relationships": [...],
    "marriage": {
      "prediction": "...",
      "partner_traits": [...],
      "challenges": "..."
    },
    "romantic_influences": "..."
  }
}""",
            "health_and_wellbeing": """
You are a Vedic astrology expert. Analyze the birth chart for health insights:
Return JSON:
{
  "health_and_wellbeing": {
    "concerns": [...],
    "recommendations": [...],
    "long_term_health": "..."
  }
}""",
            "challenges_and_remedies": """
You are a Vedic astrology expert. Analyze the birth chart:
Return JSON:
{
  "challenges_and_remedies": {
    "challenges": [...],
    "remedies": {
      "mantras": [...],
      "spiritual_practices": [...],
      "astrological_recommendations": [...]
    }
  }
}""",
            "major_life_periods": """
You are a Vedic astrology expert. Analyze the birth chart for key life stages:
Return JSON:
{
  "major_life_periods": {
    "early_life": "...",
    "mid_life": "...",
    "later_years": "..."
  }
}""",
            "today_reading": """
You are a Vedic astrology expert. Provide today's reading:
JSON:
{
  "today_reading": {
    "general_insights": "...",
    "color_of_the_day": "...",
    "favorable_activities": [...],
    "challenging_aspects": [...],
    "remedies_for_the_day": [...]
  }
}""",
        }

    def generate_reading(self, user: Any, reading_type: str = "today_reading") -> Dict[str, Any]:
        """
        Generate a reading by:
         1. Loading (or creating) the user's birth chart data
         2. Passing a relevant prompt + chart info to OpenAI
         3. Parsing and returning the structured JSON
        """

        # If user has no stored birth chart, we try to compute it using AstroService
        # Assuming you store date_of_birth/time_of_birth/place_of_birth in user profile or user model
        date_of_birth = getattr(user, "date_of_birth", None)
        time_of_birth = getattr(user, "time_of_birth", None)  # might be separate or combined
        place_of_birth = getattr(user, "place_of_birth", "48.8566,2.3522")

        if not date_of_birth or not time_of_birth:
            # fallback
            logger.warning("User birth info missing; using fallback.")
            birth_chart = {}
        else:
            birth_chart = self.astro_service.calculate_birth_chart(
                date_of_birth=date_of_birth,
                time_of_birth=time_of_birth,
                place_of_birth=place_of_birth,
            )

        # Construct the prompt
        base_prompt = self.prompts.get(reading_type, self.prompts["today_reading"])
        content = (
            f"This is the user's birth chart:\n{birth_chart}\n\n"
            f"Provide a detailed reading:\n\n{base_prompt}"
        )

        # Send to OpenAI
        messages = [
            {"role": "system", "content": "You are a helpful Vedic astrology assistant."},
            {"role": "user", "content": content},
        ]
        response = self.openai_api.chat_completion(messages)

        # Save reading in DB for historical record
        # The Reading model is called UserReading in predictions/models.py
        reading_obj = UserReading.objects.create(
            user=user,
            reading_type=reading_type,
            content=response if isinstance(response, dict) else {"raw": str(response)},
        )

        return reading_obj.content
