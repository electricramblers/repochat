import streamlit as st
import time
import os
import subprocess
import sys
import traceback
import json
import yaml
from git.exc import GitCommandError
from termcolor import colored


from altPages import index, viewEditConfiguration
from multipage import MultiPage

from repochat.git import (
    clone_repository,
    post_clone_actions,
    pre_clone_actions,
    all_repository_actions,
)
from repochat.db import (
    vector_db,
)


from repochat.models import ai_agent, model_chooser
from repochat.configmaker import create_yaml_file
from repochat.chain import parentChildChain
from repochat.multiQueryChain import multiQuery

from repochat.constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
    get_current_time_date,
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


def main_window_spinner(function, message):
    with st.spinner(message):
        result = function
        time.sleep(3)


def extract_model_name():
    result = ai_agent()
    # Iterate through each item in the tuple
    for item in result:
        # Check if the item is an instance of a class with a __dict__ attribute
        if hasattr(item, "__dict__"):
            # Iterate through the dictionary of the item
            for key, value in item.__dict__.items():
                # Check if the key is 'model_name'
                if key == "model_name":
                    # Return the value associated with 'model_name'
                    return value
    return None


def chat_current_time_date(chat_history):
    current_time_date = get_current_time_date()
    chat_history.append(current_time_date)
    return chat_history


def sidebar_model():
    model_in_use = extract_model_name()
    model_type = st.session_state.model_type
    if model_type == "local":
        st.sidebar.success("Local AI")
    elif model_type == "remote":
        st.sidebar.warning("Network AI")
    elif model_type == "openrouter":
        st.sidebar.error(f"OpenRouter")
        st.write(model_in_use)


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


def run_helper():
    os.chdir(os.path.dirname(__file__))
    subprocess.call(["python", "helper.py"])
    path = "prompt.txt"
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


def sidebar_custom_css():
    st.markdown(
        """
        <style>
        /* This affects all text within the Streamlit app */
        html, body, [class*="st-"] {
            font-size: 18px;
        }
        /* This specifically affects chat messages */
        .stChatMessage {
            font-size: 18px;
        }
        /* This specifically affects the sidebar */
        .stSidebar, .stSidebar-content {
            font-size: 10px;
        }
        /* This specifically affects markdown text */
        .markdown-text-container {
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
        st.session_state.clone_repository = False
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = False
    if "conversation" not in st.session_state:
        st.session_state.conversation = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # Initialize chat_history as an empty list


def page_config():
    st.set_page_config(
        page_title="The Amazing Articulate Automaton of Assemblege",
        page_icon=":scroll:",
    )
    apply_custom_css()


# -------------------------------------------------------------------------------
# Handle all user input
# -------------------------------------------------------------------------------


def handle_user_input(user_input):
    # Get the current time and date
    current_time_and_date = f" The current time and date is: {get_current_time_date()}"

    # Append the current time and date to the user input for processing
    expanded_user_input = user_input  # + current_time_and_date

    # Send the modified input to the LLM
    # Line 130 multiQuerychain.py
    response = st.session_state.conversation({"question": expanded_user_input})

    # Append only the original user input to the chat history
    st.session_state.chat_history.append(user_input)

    # Append the assistant's response to the chat history
    st.session_state.chat_history.append(response["answer"])

    # Display the chat history
    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            with st.chat_message("user"):
                st.write(message)
        else:
            with st.chat_message("assistant"):
                st.write(message)


# -------------------------------------------------------------------------------
# Multipage App Definitions
# -------------------------------------------------------------------------------


def multipages():
    app = MultiPage()
    app.add_page("Home", index.app)
    app.add_page("View/Edit Configuration", viewEditConfiguration.app)
    app.run()


# -------------------------------------------------------------------------------
# Sidebar definition
# -------------------------------------------------------------------------------


def sidebar_function():
    github_url = configuration()["github"]["url"]
    github_branch = configuration()["github"]["branch"]
    with st.sidebar:
        st.sidebar.markdown(f"# Repository:")
        repo_path = absolute_path_to_repo_directory()
        if os.path.exists(repo_path):
            st.sidebar.write(f"{github_url}")
            st.sidebar.caption(
                f"<strong>Branch:</strong> {github_branch}", unsafe_allow_html=True
            )
        else:
            st.sidebar.write(f"Repository needs cloned.")
            st.sidebar.caption(f"<strong>Branch:</strong> None", unsafe_allow_html=True)
        st.divider()
        conversation_history_on = st.toggle(
            "Conversation history.",
            value=False,
        )

        st.button(
            f"Clone Repository",
            use_container_width=True,
            on_click=lambda: main_window_spinner(
                all_repository_actions(), "Cloning Repository..."
            ),
        )

        st.divider()
        if configuration()["developer"]["debug"]:
            st.sidebar.button("Meta Helper", on_click=lambda: run_helper())
        st.sidebar.divider()
        # ----------------------------------------------------------------------
        # Temporary Messages
        # ----------------------------------------------------------------------

        if conversation_history_on and not st.session_state.conversation_history:
            display_temporary_message("Conversation history activated!")
            st.session_state.conversation_history = True
        else:
            st.session_state.conversation_history = False
        if clone_repository and not st.session_state.clone_repository:
            display_temporary_message("Repository cloned!")
            st.session_state.clone_repository = True


# -------------------------------------------------------------------------------
# Streamlit Main Function
# -------------------------------------------------------------------------------
def streamlit_init():
    return


# -------------------------------------------------------------------------------
# Here Be Dragons
# -------------------------------------------------------------------------------


def main():
    init()
    page_config()
    multipages()
    sidebar_function()
    streamlit_init()
    return


if __name__ == "__main__":
    main()
