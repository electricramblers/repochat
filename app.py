import streamlit as st
from git.exc import GitCommandError
from repochat.git import clone_repository, post_clone_actions
from repochat.db import vector_db, hf_embeddings, load_to_db
from repochat.constants import (
    absolute_path_to_repo_directory,
    configuration,
)
import time

# -------------------------------------------------------------------------------
# Streamlit Functions
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
        hf_embeddings(),
        load_to_db(absolute_path_to_repo_directory()),
    )
    return True


def display_temporary_message(message):
    placeholder = st.empty()
    placeholder.success(message)
    time.sleep(2)
    placeholder.empty()


def streamlit_function():
    config = configuration()
    github_url = config["github"]["url"]
    github_branch = config["github"]["branch"]

    # Use cached functions here instead of threading
    if not st.session_state.get("clone_done"):
        try:
            with st.spinner("Attempting to clone the repository."):
                if cached_clone_repository():
                    st.session_state["clone_done"] = True
                    display_temporary_message(
                        "Repository cloned and processed successfully"
                    )
        except GitCommandError as e:
            st.error(f"Error cloning repository: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

    if not st.session_state.get("prune_done"):
        try:
            with st.spinner("Attempting to prune the repository."):
                if cached_post_clone_actions():
                    st.session_state["prune_done"] = True
                    display_temporary_message("Repository pruned successfully")
        except GitCommandError as e:
            st.error(f"Error pruning repository: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

    if not st.session_state.get("ingest_done"):
        try:
            with st.spinner("Attempting to create the database."):
                if cached_create_database():
                    st.session_state["ingest_done"] = True
                    display_temporary_message("Database created successfully")
        except GitCommandError as e:
            st.error(f"Error creating database: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

    st.title("Hello World App")
    st.sidebar.markdown(f"# Repository:")
    st.sidebar.write(f"{github_url}")
    st.sidebar.markdown(
        f"<strong>Branch:</strong> {github_branch}", unsafe_allow_html=True
    )
    user_input = st.text_input("Enter some text")
    st.write("You entered:", user_input)


def main():
    streamlit_function()


if __name__ == "__main__":
    main()
