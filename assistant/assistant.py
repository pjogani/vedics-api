import time

from assistant.openai_utils import OpenAIAPI
from core.conduit.utils import get_structure_openai_response




def get_assistant_response(thread_id, assistant_id):
    openai_wrapper = OpenAIAPI()
    run = openai_wrapper.run_assistant_on_thread(thread_id, assistant_id)
    count = 0
    while 1:
        run_status = get_run_status(thread_id, run.id)
        if run.status == "completed" or run_status == "completed":
            message = list_latest_message(thread_id)
            return get_structure_openai_response(message)
        if run_status == "failed":
            break
        time.sleep(0.5)
        count += 1
        if count == 60:
            break
    return {"reply": "Sorry, I'm having trouble generating your reading. Please try again later."}


def get_run_status(thread_id, run_id):
    openai_wrapper = OpenAIAPI()
    run_retrieve = openai_wrapper.get_run_status(thread_id, run_id)
    return run_retrieve.status


def list_latest_message(thread_id):
    openai_wrapper = OpenAIAPI()
    messages = openai_wrapper.list_messages(thread_id)
    return messages.data[0].content[0].text.value
