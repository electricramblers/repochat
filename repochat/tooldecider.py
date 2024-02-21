import os
import yaml
from termcolor import colored
from datetime import datetime
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from .constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
    get_current_time_date,
)


# Add the new tool to the list of tools
tools = [
    Tool(
        name="Datetime",
        func=lambda x: get_current_time_date(),
        description="Returns the current datetime",
    ),
]

# Initialize the agent with the new tool
agent = initialize_agent(
    tools,
    fake_llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    **kwargs,
)
