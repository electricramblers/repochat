import streamlit as st
import time
import os
import subprocess
import sys
import json
import yaml
from git.exc import GitCommandError
from termcolor import colored
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

from repochat.git import clone_repository, post_clone_actions, pre_clone_actions
from repochat.db import (
    embedding_chooser,
    get_first_true_embedding,
    load_code,
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


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


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
    if "pre_clone_actions" not in st.session_state:
        st.session_state.pre_clone_actions = False
    if "clone_repository" not in st.session_state:
        st.session_state.clone_repository = None
    if "post_clone_actions" not in st.session_state:
        st.session_state.post_clone_actions = False
    if "vector_database" not in st.session_state:
        st.session_state.vector_database = False
    if "analyze_code" not in st.session_state:
        st.session_state.analyze_code = None
    if "conversation" not in st.session_state:
        st.session_state.conversation = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # Initialize chat_history as an empty list


def page_config():
    st.set_page_config(
        page_title="The Amazing Articulate Automaton of Assemblege",
        page_icon=":scroll:",
    )


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
    # Pre clone activities
    # -------------------------------------------------------------------------------

    if not st.session_state.get("pre_clone_actions"):
        try:
            with st.spinner("Attempting to remove directories."):
                if pre_clone_actions():
                    st.session_state["pre_clone_actions"] = True
                    display_temporary_message("Directories removed successfully")
        except GitCommandError as e:
            st.error(f"Error removing directories: {str(e)}")
        except Exception as e:
            st.error(f"line 278 app.py - Unexpected error: {str(e)}")

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
    # Create the vector database
    # -------------------------------------------------------------------------------
    if not st.session_state.get("vector_database"):
        try:
            with st.spinner("Attempting to create the database."):
                if vector_db():
                    st.session_state["vector_database"] = True
                    display_temporary_message("Database created successfully.")
        except GitCommandError as e:
            st.error(f"Error creating database: {str(e)}")
        except Exception as e:
            st.error(f"line 314 app.py -Unexpected error: {str(e)}")

    # -------------------------------------------------------------------------------
    # Analyze the code
    # -------------------------------------------------------------------------------
    if not st.session_state.get("analyze_code"):
        try:
            with st.spinner("Database Operation. This may take some time..."):
                mq = multiQuery()
                if mq.analyze_code(load_code()):
                    st.session_state["analyze_code"] = True
                    display_temporary_message("Code Analyzed Successfully")
        except GitCommandError as e:
            st.error(f"Error analyzing code repository: {str(e)}")
        except Exception as e:
            st.error(f"line 329 in app.py - Unexpected error: {str(e)}")

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
        st.sidebar.caption(
            f"<strong>Branch:</strong> {github_branch}", unsafe_allow_html=True
        )
        st.divider()
        st.sidebar.button(
            "Edit Config", on_click=lambda: open_config_file(absolute_path_to_config())
        )
        if configuration()["developer"]["debug"]:
            st.sidebar.button("Meta Helper", on_click=lambda: run_helper())
            st.sidebar.divider()
    return


# -------------------------------------------------------------------------------
# Here Be Dragons
# -------------------------------------------------------------------------------


def main():
    create_config_if_missing()
    init()
    page_config()
    sidebar_custom_css()
    streamlit_init()
    return


if __name__ == "__main__":
    main()
