import streamlit as st
import time

from repochat.git import clone_repository, post_clone_actions
from repochat.db import vector_db, load_to_db, embedding_chooser
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


# Cache the clone repository action
@st.cache_data()
def cached_clone_repository():
    clone_repository()
    return True


# Cache the post clone actions
@st.cache_data()
def cached_post_clone_actions():
    post_clone_actions()
    return True


# Cache the database creation
@st.cache_data()
def cached_create_database():
    vector_db(
        embedding_chooser(),
        load_to_db(absolute_path_to_repo_directory()),
    )
    return True


def display_temporary_message(message):
    placeholder = st.empty()
    placeholder.success(message)
    time.sleep(2)
    placeholder.empty()


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


def init():
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "llm" not in st.session_state:
        st.session_state.llm = ai_agent()
    if "embeddings" not in st.session_state:
        st.session_state.embeddings = embedding_chooser()


def streamlit_init():
    st.set_page_config(
        page_title="The Amazing Articulate Automaton of Assemblege", page_icon=":books:"
    )
    st.write(css, unsafe_allow_html=True)

    st.header(":books: Förderrichtlinien-Assistent ")
    user_input = st.chat_input("Foo")
    if user_input:
        with st.spinner("Processing..."):
            handle_user_input(user_input)

    with st.sidebar:
        st.subheader("funding guidlines")
        pdf_docs = st.file_uploader("upload documents here", accept_multiple_files=True)
        if st.button("upload"):
            with st.spinner("analyzing documents"):
                analyze_documents(pdf_docs)
    return
