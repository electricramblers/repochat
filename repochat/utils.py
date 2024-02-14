import os
import re
import shutil
import subprocess
import streamlit as st


from .constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
)


def init_session_state():
    SESSION_DEFAULTS = {
        "messages": [],
        "chroma_db": None,
        "db_loaded": False,
        "repo_path": f"{absolute_path_to_repo_directory()}",
        "git_form": False,
        "qa": None,
        "db_name": None,
    }

    for keys, values in SESSION_DEFAULTS.items():
        if keys not in st.session_state:
            st.session_state[keys] = values


def url_name(url):
    pattern = r"https?://github.com/([^/]+)/([^/]+)"
    match = re.match(pattern, url)
    if match:
        owner = match.group(1)
        repo = match.group(2)
        return f"{owner}_{repo}"
    else:
        st.error("Enter valid GitHub URL")
        st.stop()


def clone_repo(git_url, repo_path, branch="main"):
    """
    Clone a git repository to the specified path.
    """
    try:
        Repo.clone_from(git_url, repo_path, branch=branch)
    except GitCommandError as e:
        raise ValueError(f"Error cloning repository: {e}") from None
    except Exception as e:
        print(colored(f"Error cloning repository: {e}", "red"))
        return

    try:
        print(colored("FUCK NO", "red"))
        # Fetching repository details
        repo_name = repository_name_only()
        token = configuration()["github"]["token"]
        username = configuration()["github"]["username"]
        target_folder = absolute_path_to_database_directory()

        # Setting up config
        config = {
            "github": {
                "username": username,
                "repo_name": repo_name,
                "token": token,
            }
        }

        repo_url = f"https://api.github.com/repos/{config['github']['username']}/{config['github']['repo_name']}?access_token={config['github']['token']}"

        # Creating target directory if not exists
        os.makedirs(target_folder, exist_ok=True)
        os.chdir(target_folder)

        try:
            req_json = requests.get(repo_url).json()
            repo_git_url = req_json["git_url"]
            os.system(f"git clone {repo_git_url}")
        except requests.exceptions.RequestException as e:
            print(colored(f"Error: {e}", "red"))
            # Handle error as per requirement
    except Exception as e:
        print(colored(f"Error: {e}", "red"))


def prompt_format(system_prompt, instruction):
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<SYS>>\n", "\n<</SYS>>\n\n"
    SYSTEM_PROMPT = B_SYS + system_prompt + E_SYS
    prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
    return prompt_template


def model_prompt():
    system_prompt = """You are a helpful assistant, you have good knowledge in coding and you will use the provided context to answer user questions with detailed explanations.
    Read the given context before answering questions and think step by step. If you can not answer a user question based on the provided context, inform the user. Do not use any other information for answering user"""
    instruction = """
    Context: {context}
    User: {question}"""
    return prompt_format(system_prompt, instruction)


def custom_que_prompt():
    que_system_prompt = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question and give only the standalone question as output in the tags <question> and </question>.
    """

    instr_prompt = """Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""

    return prompt_format(que_system_prompt, instr_prompt)
