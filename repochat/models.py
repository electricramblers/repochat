import requests
import os
import subprocess
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
    except:
        pass
    try:
        print(colored("Trying a remote ollama model.", "cyan"))
        response = requests.get(config["models"]["ollama"]["base_url"])
        if response.status_code == 200:
            ai_model = config["models"]["ollama"]["remote"]
            base_url = config["models"]["ollama"]["base_url"]
            model_to_use = Ollama(model=ai_model, base_url=str(base_url))
            return model_to_use
        else:
            raise Exception(
                colored(
                    "Failed to get a successful response from the remote model.", "red"
                )
            )
    except:
        pass


class OpenRouterLLM:
    n: int

    @property
    def _llm_type(self) -> str:
        """Return the LLM type."""
        return f"{OPENROUTERMODEL}"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Mixtral LLM with the given prompt."""
        YOUR_SITE_URL = "https://localhost"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": YOUR_SITE_URL,
            "Content-Type": "application/json",
        }
        data = {
            "model": f"{OPENROUTERMODEL}",
            "messages": [{"role": "user", "content": prompt}],
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
        )
        output = response.json()["choices"][0]["message"]["content"]

        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        return output

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"n": self.n}


def ai_agent():
    ai_model = model_chooser()
    config = configuration()
    callbackmanager = CallbackManager([StreamingStdOutCallbackHandler()])
    llm = ai_model
    return llm
