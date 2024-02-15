import requests
import os
from termcolor import colored
from typing import Any, List, Mapping, Optional
from .constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
)


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
