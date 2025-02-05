import os
import re
import json
import logging

import openai
from django.conf import settings

logger = logging.getLogger(__name__)

# Read API key from environment or Django settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") or getattr(settings, "OPENAI_API_KEY", None)
openai.api_key = OPENAI_API_KEY


def get_structure_openai_response(ai_response: str):
    """
    Attempt to parse the LLM response as valid JSON or best-effort transform into a dict/list.

    1) Strips triple backticks if present.
    2) Converts Python booleans/None to JSON equivalents.
    3) Attempts to unify single quotes around JSON keys/values into double quotes.
    4) If everything fails, returns the raw string for debugging.
    """
    # Trim whitespace
    ai_response = ai_response.strip()

    # Remove enclosing triple backticks if present (e.g., ```json ... ```)
    fence_pattern = re.compile(r"^```[a-zA-Z]*\s*([\s\S]+?)\s*```$")
    match = fence_pattern.match(ai_response)
    if match:
        ai_response = match.group(1).strip()

    # Remove extra quotes if the entire string is in single/double quotes
    if (ai_response.startswith('"') and ai_response.endswith('"')) or (
        ai_response.startswith("'") and ai_response.endswith("'")
    ):
        if len(ai_response) > 1:
            ai_response = ai_response[1:-1].strip()

    # Replace Python-specific tokens with JSON
    ai_response = ai_response.replace("None", "null")
    ai_response = ai_response.replace("True", "true")
    ai_response = ai_response.replace("False", "false")

    # Attempt a basic single-quote -> double-quote fix for keys/values
    single_quote_key_value_pattern = re.compile(r"([{\[,]\s*)'([^'\r\n]+)'\s*([},\]:])")
    while True:
        new_response = single_quote_key_value_pattern.sub(r'\1"\2"\3', ai_response)
        if new_response == ai_response:
            break
        ai_response = new_response

    # Attempt to parse as JSON
    try:
        return json.loads(ai_response)
    except Exception:
        pass

    # If everything fails, just return raw text
    return ai_response


class OpenAIAPI:
    """
    A wrapper around OpenAI's completion and embedding APIs.
    """

    def __init__(self):
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not set; requests will fail.")

    def chat_completion(self, messages, model="gpt-3.5-turbo", temperature=0.7):
        """
        Given a list of messages (Django-style: [{"role":"user","content":"..."}]),
        call the OpenAI ChatCompletion API and return the assistant's content as a string.
        """

        if not OPENAI_API_KEY:
            return "OpenAI API key is missing. Please set OPENAI_API_KEY."

        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            ai_response = response.choices[0].message["content"]
            structured = get_structure_openai_response(ai_response)
            return structured
        except Exception as e:
            logger.error(f"OpenAI chat_completion error: {str(e)}")
            return {"error": "OpenAI request failed", "detail": str(e)}

    def generate_embedding(self, text, model="text-embedding-ada-002"):
        """
        Generate an embedding vector for the provided text using the OpenAI embedding API.
        Returns a list of floats, or None on error.
        """
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key is missing.")
            return None

        try:
            res = openai.Embedding.create(input=text, model=model)
            return res["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"OpenAI generate_embedding error: {str(e)}")
            return None
