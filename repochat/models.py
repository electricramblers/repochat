import requests
import os
import socket
import subprocess
import urllib.parse
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.manager import CallbackManager, CallbackManagerForLLMRun
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain_community.llms import Ollama
from termcolor import colored
from typing import Any, List, Mapping, Optional
from .constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
)


def hf_embeddings():
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
    )


def model_chooser():
    config = configuration()
    print(colored("Trying a local ollama model.", "cyan"))
    try:
        subprocess.check_output(["ollama", "--version"])
        local_ollama = True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        local_ollama = False
        print(colored(f"Local ollama failed. Error: {e}", "cyan"))
    try:
        print(colored("Trying remote ollama model.", "cyan"))
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
        print(colored(f"Remote ollama failed. Error: {e}", "cyan"))
        remote_ollama = False
    if local_ollama:
        ai_model = config["models"]["ollama"]["local"]
        model_to_use = Ollama(model=ai_model)
        print(colored("Local Ollama Success", "cyan"))
        return model_to_use
    elif remote_ollama:
        ai_model = config["models"]["ollama"]["remote"]
        remote_url = config["models"]["ollama"]["base_url"]
        model_to_use = Ollama(model=ai_model, base_url=remote_url)
        print(colored("Remote Ollama: Success", "cyan"))
        return model_to_use
    else:
        print(colored("Error. No AI Model Available.", "red"))
        exit(1)


def ai_agent():
    ai_model = model_chooser()
    config = configuration()
    callbackmanager = CallbackManager([StreamingStdOutCallbackHandler()])
    llm = ai_model
    return llm
