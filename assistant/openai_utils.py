import os
from datetime import datetime

from django.conf import settings
import openai

from core.conduit.utils import get_structure_openai_response

# Read API key from environment or Django settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") or getattr(settings, "OPENAI_API_KEY", None)
openai.api_key = OPENAI_API_KEY



class CompletionClient:
    def __init__(self, metadata=None, use_openai_client=False):
        self.client = self._initialize_client(metadata, use_openai_client)

    @classmethod
    def get_instance(cls, metadata=None, user_openai_client=False):
        return CompletionClient(metadata, user_openai_client)

    def _initialize_client(self, metadata, use_openai_client=False):
        return openai

    def extract_ai_response(self, response):

        ai_response_dict = response.choices[0].message
        ai_response = (
            ai_response_dict["content"]
            if isinstance(ai_response_dict, dict)
            else ai_response_dict.content
        )

        return get_structure_openai_response(ai_response)

    def generate_extracted_info(self, messages, model_name="gpt-4o"):
        try:
            gpt_data = {
                "model": model_name,
                "messages": messages,
                "response_format": {"type": "json_object"},
            }

            response = self.client.chat.completions.create(**gpt_data)
            ai_response_json = self.extract_ai_response(response)

            return {"status": "SUCCESS", "response": ai_response_json}

        except Exception as e:
            return {
                "status": "FAILED",
                "response": {},
                "error_description": str(e),
            }

    def generate_info(
        self,
        prompt,
        content,
        model_name="gpt-4o",
        return_prompt=False,
    ):
        content = content.replace("  ", " ").replace("NaN", " ").replace("NaT", " ")
        while "  " in content:
            content = content.replace("  ", " ")

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content},
        ]

        result = self.generate_extracted_info(messages, model_name)
        if return_prompt:
            result["prompt"] = prompt

        return result


class AssistantClient:
    def __init__(self, client):
        self.client = client

    @classmethod
    def get_instance(cls, client):
        return AssistantClient(client)

    def list_assistants(self):
        return self.client.beta.assistants.list(order="desc", limit="20")

    def create_assistant(self, name, instruction, tools=None, model="gpt-4o"):
        return self.client.beta.assistants.create(
            name=name,
            instructions=instruction,
            model=model,
            tools=tools,
        )

    def modify_assistant(self, assistant_id, name, instruction, model="gpt-4o"):
        return self.client.beta.assistants.update(
            assistant_id,
            name=name,
            instructions=instruction,
            model=model,
        )

    def add_file_to_assistant(self, assistant_id, file_path):
        file = self.client.files.create(file=open(file_path, "rb"), purpose="assistants")
        return self.client.beta.assistants.files.create(assistant_id=assistant_id, file_id=file.id)


class ThreadClient:
    def __init__(self, client):
        self.client = client

    @classmethod
    def get_instance(cls, client):
        return ThreadClient(client)

    def create_thread(self, metadata={}):
        return self.client.beta.threads.create(metadata=metadata)

    def retrieve_thread(self, thread_id):
        return self.client.beta.threads.retrieve(thread_id)

    def add_message_to_thread(self, thread_id, content, metadata={}):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"{current_time}: {content}"
        return self.client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=str(content), metadata=metadata
        )

    def list_messages(self, thread_id, limit=100):
        return self.client.beta.threads.messages.list(thread_id, limit=limit)

    def run_assistant_on_thread(self, thread_id, assistant_id):
        return self.client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

    def get_run_status(self, thread_id, run_id):
        return self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)


class EmbeddingClient:
    def __init__(self, client):
        self.client = client

    @classmethod
    def get_instance(cls, client):
        return EmbeddingClient(client)

    def generate_embedding(self, text):
        response = self.client.embeddings.create(input=text, model="text-embedding-3-small")
        return response.data[0].embedding


class OpenAIAPI:
    def __init__(self, metadata={}, use_openai_client=False):
        self.completion_client = CompletionClient.get_instance(metadata, use_openai_client)
        self.assistant_client = AssistantClient.get_instance(self.completion_client.client)
        self.thread_client = ThreadClient.get_instance(self.completion_client.client)
        self.embedding_client = EmbeddingClient.get_instance(self.completion_client.client)

    def generate_extracted_info(self, *args, **kwargs):
        return self.completion_client.generate_info(*args, **kwargs)

    def list_assistants(self, *args, **kwargs):
        return self.assistant_client.list_assistants(*args, **kwargs)

    def create_assistant(self, *args, **kwargs):
        return self.assistant_client.create_assistant(*args, **kwargs)

    def modify_assistant(self, *args, **kwargs):
        return self.assistant_client.modify_assistant(*args, **kwargs)

    def add_file_to_assistant(self, *args, **kwargs):
        return self.assistant_client.add_file_to_assistant(*args, **kwargs)

    def create_thread(self, *args, **kwargs):
        return self.thread_client.create_thread(*args, **kwargs)

    def retrieve_thread(self, *args, **kwargs):
        return self.thread_client.retrieve_thread(*args, **kwargs)

    def add_message_to_thread(self, *args, **kwargs):
        return self.thread_client.add_message_to_thread(*args, **kwargs)

    def list_messages(self, *args, **kwargs):
        return self.thread_client.list_messages(*args, **kwargs)

    def run_assistant_on_thread(self, *args, **kwargs):
        return self.thread_client.run_assistant_on_thread(*args, **kwargs)

    def get_run_status(self, *args, **kwargs):
        return self.thread_client.get_run_status(*args, **kwargs)

    def generate_embedding(self, *args, **kwargs):
        return self.embedding_client.generate_embedding(*args, **kwargs)
