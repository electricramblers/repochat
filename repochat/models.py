import requests
import os
import subprocess
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from termcolor import colored
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
    model_to_use = None
    model = None
    base_url = None
    try:
        print(colored("Trying a local ollama model.", "cyan"))
        output = subprocess.check_output(["ollama", "--version"])
        ai_model = config["models"]["ollama"]["local"]
        base_url = None
        model_to_use = Ollama(model=ai_model)
        print(colored("Success...", "cyan"))
        return model_to_use
    except subprocess.CalledProcessError:
        pass
    try:
        print(colored("Trying a remote ollama model.", "cyan"))
        response = requests.get(config["models"]["ollama"]["base_url"])
        if response.status_code == 200:
            ai_model = config["models"]["ollama"]["remote"]
            base_url = config["models"]["ollama"]["base_url"]
            model_to_use = Ollama(model=ai_model, base_url=base_url)
            return model_to_use
        else:
            raise Exception(
                colored(
                    "Failed to get a successful response from the remote model.", "red"
                )
            )
    except:
        pass


def ai_agent():
    ai_model = model_chooser()
    config = configuration()
    callbackmanager = CallbackManager([StreamingStdOutCallbackHandler()])
    llm = ai_model
    return llm
