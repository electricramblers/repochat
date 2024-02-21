import streamlit as st
import time
import os
import subprocess
import sys
from git.exc import GitCommandError
from termcolor import colored
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from repochat.git import clone_repository, post_clone_actions
from repochat.db import embedding_chooser, load_code
from repochat.models import ai_agent, model_chooser
from repochat.configmaker import create_yaml_file


from repochat.chain import (
    response_chain,
    get_retriever,
    get_retriever,
    get_conversation,
    analyze_code,
)

from repochat.constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
)

# -------------------------------------------------------------------------------
# Create a generic config.yaml if it is not there
# -------------------------------------------------------------------------------


def create_config_if_missing():
    if not os.path.exists(absolute_path_to_config()):
        create_yaml_file()


# -------------------------------------------------------------------------------
# Streamlit Addon Functions
# -------------------------------------------------------------------------------


def sidebar_model():
    model_type = st.session_state.model_type
    if model_type == "local":
        st.sidebar.success("Local AI")
    elif model_type == "remote":
        st.sidebar.warning("Network AI")
    elif model_type == "openrouter":
        st.sidebar.error("OpenRouter")


def open_config_file(path):
    try:
        if sys.platform.startswith("darwin"):  # macOS
            subprocess.run(["open", path], check=True)
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", path], check=True)
        elif sys.platform.startswith("win32") or sys.platform.startswith("cygwin"):
            os.startfile(path)
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"Failed to open the file: {e}")


def display_temporary_message(message):
    placeholder = st.empty()
    placeholder.success(message)
    time.sleep(2)
    placeholder.empty()


# -------------------------------------------------------------------------------
# Custom CSS
# -------------------------------------------------------------------------------
def apply_custom_css():
    st.markdown(
        """
        <style>
        /* This affects all text within the Streamlit app */
        html, body, [class*="st-"] {
            font-size: 18px;
        }
        /* This specifically affects markdown text */
        .markdown-text-container {
            font-size: 18px;
        }
        /* This specifically affects chat messages */
        .stChatMessage {
            font-size: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------------
# Functions that are needed to initialize streamlit.
# -------------------------------------------------------------------------------
def init():
    if "clone_repository" not in st.session_state:
        st.session_state.clone_repository = None
    if "post_clone_actions" not in st.session_state:
        st.session_state.post_clone_actions = None
    if "analyze_code" not in st.session_state:
        st.session_state.analyze_code = None
    if "conversation" not in st.session_state:
        st.session_state.conversation = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "llm" not in st.session_state or "model_type" not in st.session_state:
        st.session_state.llm, st.session_state.model_type = ai_agent()
    if "embeddings" not in st.session_state:
        st.session_state.embeddings = embedding_chooser()
    st.set_page_config(
        page_title="The Amazing Articulate Automaton of Assemblege",
        page_icon=":scroll:",
    )


# -------------------------------------------------------------------------------
# Handle all user input
# -------------------------------------------------------------------------------
def handle_user_input(user_input):
    response = st.session_state.conversation({"question": user_input})
    st.session_state.chat_history = response["chat_history"]

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            with st.chat_message("user"):
                st.write(message.content)
        else:
            with st.chat_message("assistant"):
                st.write(message.content)


# -------------------------------------------------------------------------------
# Streamlit Main Function
# -------------------------------------------------------------------------------
def streamlit_init():
    # -------------------------------------------------------------------------------
    # Configuraiton
    # -------------------------------------------------------------------------------
    config = configuration()
    github_url = config["github"]["url"]
    github_branch = config["github"]["branch"]

    # -------------------------------------------------------------------------------
    # Main streamlit application
    # -------------------------------------------------------------------------------
    st.header(":scroll: The Amazing Articulate Automaton of Assemblege")

    # -------------------------------------------------------------------------------
    # Cloning the repository
    # -------------------------------------------------------------------------------
    if not st.session_state.get("clone_repository"):
        try:
            with st.spinner("Attempting to clone the repository."):
                if clone_repository():
                    st.session_state["clone_repository"] = True
                    display_temporary_message(
                        "Repository cloned and processed successfully"
                    )
        except GitCommandError as e:
            st.error(f"Error cloning repository: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

    # -------------------------------------------------------------------------------
    # Prune the cloned database
    # -------------------------------------------------------------------------------

    if not st.session_state.get("post_clone_actions"):
        time.sleep(2)
        try:
            with st.spinner("Attempting to prune the repository."):
                if post_clone_actions():
                    st.session_state["post_clone_actions"] = True
                    display_temporary_message("Repository pruned successfully")
        except GitCommandError as e:
            st.error(f"Error pruning repository: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

    # -------------------------------------------------------------------------------
    # Analyze the code
    # -------------------------------------------------------------------------------

    if not st.session_state.get("analyze_code"):
        try:
            with st.spinner("Attempting to Analyze Code."):
                if analyze_code(load_code()):
                    print(colored(f"line 166 app.py - code is {code}", "white"))
                    st.session_state["analyze_code"] = True
                    display_temporary_message("Code Analyzed Successfully")
        except GitCommandError as e:
            st.error(f"Error analyzing code repository: {str(e)}")
        except Exception as e:
            st.error(f"line 171 in app.py - Unexpected error: {str(e)}")

    # -------------------------------------------------------------------------------
    # User Input
    # -------------------------------------------------------------------------------

    user_input = st.chat_input("Enter you question or query.")
    if user_input:
        with st.spinner("Processing..."):
            handle_user_input(user_input)

    # -------------------------------------------------------------------------------
    # sidebar application
    # -------------------------------------------------------------------------------

    with st.sidebar:
        sidebar_model()
        st.sidebar.markdown(f"# Repository:")
        st.sidebar.write(f"{github_url}")
        st.sidebar.markdown(
            f"<strong>Branch:</strong> {github_branch}", unsafe_allow_html=True
        )
        st.sidebar.button(
            "Edit Config", on_click=lambda: open_config_file(absolute_path_to_config())
        )
    return


# -------------------------------------------------------------------------------
# Here Be Dragons
# -------------------------------------------------------------------------------


def main():
    create_config_if_missing()
    init()
    apply_custom_css()
    streamlit_init()
    return


if __name__ == "__main__":
    main()
