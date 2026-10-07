import logging
import os
import tiktoken
from llm.prompt import *
import logging
import time
from my_utils.str_utils import only_ascii_clip
from func_timeout import func_set_timeout, FunctionTimedOut
# [CARBON-RETEST] The model is Gemini 2.5 Pro on Vertex AI instead of OpenAI.
from harness.gemini_client import chat as gemini_chat

logger = logging.getLogger(__name__)
logger.setLevel(1)

chat_log_dir = "../Data/Temp/chat_log/"

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")


def chatgpt(messages: list):
    log_message(messages)
    try:
        # res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, timeout=5, temperature=0)
        # res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, timeout=5)
        res = timeout_predict(messages)
        if len(res.keys()) > 0:
            response = res["choices"][0]["message"]["content"].strip()
            response = response.replace("\n\n", "\n")
            # print(response)
            log_result(response)
            return response
        else:
            return ""
    except FunctionTimedOut as e:
        print(e)
        return ""
    except Exception as e:
        print(e)
        return ""


# [CARBON-RETEST] Upstream allows 10 s per call, which suits GPT-3.5 but not
# Gemini 2.5 Pro, whose thinking regularly takes longer; a 10 s limit would turn
# most turns into empty replies. The limit is configurable and defaults to 180 s.
@func_set_timeout(float(os.environ.get("REACTDROID_LLM_TIMEOUT", "180")))
def timeout_predict(messages):
    # [CARBON-RETEST] Same messages and temperature (0) as upstream. The reply is
    # wrapped in the ChatCompletion shape that chatgpt() above reads.
    text = gemini_chat(messages, temperature=0, tag="reactdroid")
    return {"choices": [{"message": {"content": text}}]}


def get_str_len(in_str: str):
    return len(encoding.encode(in_str))

def log_message(messages: list, show_all=False):
    all_message = []
    for idx, message in enumerate(messages):
        content = message["content"].strip()
        prefix = message["role"][:4] + str(idx + 1) + ": "
        if show_all or idx == len(messages) - 1:
            if len(content.split("\n")) > 1:
                content_lines = content.split("\n")
                for line in [content_lines[0], content_lines[-1]]:
                    logger.info(prefix + only_ascii_clip(line, 20).replace("[", " ").replace("]", " "))
            else:
                logger.info(prefix + only_ascii_clip(content, 20).replace("[", " ").replace("]", " "))
        all_message.append("#" * 10 + message["role"][:4] + str(idx + 1) + "#" * 10)
        all_message.append(content)
    log_file = open(chat_log_dir + time.strftime("%m-%d_%H-%M-%S", time.localtime()) + ".txt", "w", encoding="UTF-8")
    log_file.write("\n".join(all_message))

def log_result(response: str):
    for line in response.split("\n"):
        if len(line.strip()) > 0:
            logger.info("ChatGPT Answer: " +line.strip())

if __name__ == '__main__':
    pass