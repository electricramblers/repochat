import streamlit as st
import time

from repochat.git import clone_repository, post_clone_actions
from repochat.db import embedding_chooser
from repochat.chain import response_chain
from repochat.models import ai_agent

from repochat.constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
)

# -------------------------------------------------------------------------------
# App fuctions
# -------------------------------------------------------------------------------


def reset_app_state():
    # Reset session state variables
    session_state = st.session_state
    session_state.clone_done = False
    session_state.prune_done = False
    session_state.ingest_done = False
    session_state.ready = False
    session_state.pop("chroma_db", None)
    session_state.pop("qa", None)
    session_state.pop("messages", None)


def reset_app():
    # Clear the main window
    # Reset the app state
    reset_app_state()


# -------------------------------------------------------------------------------
# Streamlit Addon Functions
# -------------------------------------------------------------------------------


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
# Streamlit UI
# -------------------------------------------------------------------------------


def init():
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "llm" not in st.session_state:
        st.session_state.llm = ai_agent()
    if "embeddings" not in st.session_state:
        st.session_state.embeddings = embedding_chooser()


def handle_user_input(question):
    response = st.session_state.conversation({"question": question})
    st.session_state.chat_history = response["chat_history"]

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            with st.chat_message("user"):
                st.write(message.content)
        else:
            with st.chat_message("assistant"):
                st.write(message.content)


def streamlit_init():
    st.set_page_config(
        page_title="The Amazing Articulate Automaton of Assemblege", page_icon=":books:"
    )
    st.write(css, unsafe_allow_html=True)

    st.header(":books: Hi there!")
    user_input = st.chat_input("Describe this application.")
    if user_input:
        with st.spinner("Processing..."):
            handle_user_input(user_input)

    with st.sidebar:
        st.subheader("Information")
    return


def main():
    init()
    apply_custom_css()
    return


if __name__ == "__main__":
    main()
