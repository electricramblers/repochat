import os
import yaml
import sys
from termcolor import colored
from io import StringIO
from typing import Dict, Optional
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents.tools import Tool
from langchain_community.chat_models import ChatOpenAI


from constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
    get_current_time_date,
)

config = configuration()
api_key = config["keys"]["openrouter"]


class ChatOpenRouter(ChatOpenAI):
    openai_api_base: str
    openai_api_key: str
    model_name: str

    def __init__(
        self,
        model_name: str,
        openai_api_key: Optional[str] = None,
        openai_api_base: str = "https://openrouter.ai/api/v1",
        **kwargs
    ):
        openai_api_key = api_key
        super().__init__(
            openai_api_base=openai_api_base,
            openai_api_key=openai_api_key,
            model_name=model_name,
            **kwargs
        )


class PythonREPL:
    """Simulates a standalone Python REPL."""

    def __init__(self):
        pass

    def run(self, command: str) -> str:
        """Run command and returns anything printed."""
        # sys.stderr.write("EXECUTING PYTHON CODE:\n---\n" + command + "\n---\n")
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(command, globals())
            sys.stdout = old_stdout
            output = mystdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            output = str(e)
        # sys.stderr.write("PYTHON OUTPUT: \"" + output + "\"\n")
        return output


llm = ChatOpenRouter(model_name="mistralai/mistral-7b-instruct:free")

python_repl = Tool(
    "Python REPL",
    PythonREPL().run,
    """A Python shell. Use this to execute python commands. Input should be a valid python command.
        If you expect output it should be printed out.""",
)
tools = [python_repl]
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
agent.run("I need a 25 character random password.")
