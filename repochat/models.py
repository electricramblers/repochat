import requests
import os
import socket
import subprocess
import urllib.parse
from langchain.callbacks.manager import CallbackManager, CallbackManagerForLLMRun
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.llms import Ollama
from termcolor import colored
from typing import Any, List, Mapping, Optional


from .constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
    get_current_time_date,
)


class OpenRouterLLM(ChatOpenAI):
    openai_api_base: str
    openai_api_key: str
    model_name: str

    def __init__(
        self,
        model_name: str,
        openai_api_key: Optional[str] = None,
        openai_api_base: str = "https://openrouter.ai/api/v1",
        **kwargs,
    ):
        super().__init__(
            openai_api_base=openai_api_base,
            openai_api_key=openai_api_key,
            model_name=model_name,
            **kwargs,
        )


def model_chooser():
    config = configuration()
    escalate = config["models"].get("escalation", True)
    if escalate:
        try:
            subprocess.check_output(["ollama", "--version"])
            local_ollama = True
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            local_ollama = False
            print(colored(f"Local ollama failed. Error: {e}", "magenta"))
    else:
        local_ollama = False
    if escalate:
        try:
            remote_ollama = config["models"]["ollama"]["base_url"]
            parsed_url = urllib.parse.urlparse(remote_ollama)
            host = parsed_url.hostname
            port = parsed_url.port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(20)
            s.connect((host, port))
            s.close()
            remote_ollama = True
        except Exception as e:
            print(colored(f"Remote ollama failed. Error: {e}", "magenta"))
            remote_ollama = False
    else:
        remote_ollama = False
    try:
        remote_openrouter = "https://openrouter.ai"
        parsed_url = urllib.parse.urlparse(remote_openrouter)
        host = parsed_url.hostname
        port = 443
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(20)
        s.connect((host, port))
        s.close()
        openrouter = True
    except Exception as e:
        openrouter = False

    if local_ollama and escalate:
        ai_model = config["models"]["ollama"]["local"]
        model_to_use = Ollama(model=ai_model)
        return model_to_use, "local"
    elif remote_ollama and escalate:
        ai_model = config["models"]["ollama"]["remote"]
        remote_url = config["models"]["ollama"]["base_url"]
        model_to_use = Ollama(model=ai_model, base_url=remote_url)
        return model_to_use, "remote"
    elif openrouter:
        ai_model = config["models"]["openrouter"]["low"]
        api_key = config["keys"]["openrouter"]
        model_to_use = OpenRouterLLM(
            model_name=ai_model,
            callbacks=[StreamingStdOutCallbackHandler()],
            openai_api_key=api_key,
        )
        return model_to_use, "openrouter"
    else:
        print(colored("Error. No AI Model Available.", "red"))
        exit(1)


def ai_agent():
    ai_model, model_type = model_chooser()
    if isinstance(ai_model, list):
        llm = ai_model[0]
    else:
        llm = ai_model
    return llm, model_type
