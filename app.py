import streamlit as st
from git.exc import GitCommandError
from repochat.git import clone_repository, post_clone_actions
from repochat.db import vector_db, hf_embeddings, load_to_db
from repochat.chain import response_chain
from repochat.models import ai_agent
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
    repo_path = absolute_path_to_repo_directory()
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

    # Ensure the database is created and cached before accessing it
    if "chroma_db" not in st.session_state or not st.session_state.get("ingest_done"):
        try:
            with st.spinner("Attempting to create the database."):
                # Call the cached_create_database function to initialize the database if not already done
                if cached_create_database():
                    st.session_state["ingest_done"] = True
                    # Assuming the vector_db function returns the database which should be stored in chroma_db
                    st.session_state["chroma_db"] = vector_db(
                        hf_embeddings(),
                        load_to_db(absolute_path_to_repo_directory()),
                    )
                    display_temporary_message("Database created successfully")
        except GitCommandError as e:
            st.error(f"Error creating database: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return  # Stop execution if database creation fails

    st.title("Hello World App")

    # -------------------------------------------------------------------------
    # Sidebar
    # -------------------------------------------------------------------------

    st.sidebar.markdown(f"# Repository:")
    st.sidebar.write(f"{github_url}")
    st.sidebar.markdown(
        f"<strong>Branch:</strong> {github_branch}", unsafe_allow_html=True
    )
    st.session_state["ready"] = True

    # -------------------------------------------------------------------------
    # Load model into membory
    # -------------------------------------------------------------------------

    if "chroma_db" in st.session_state and "qa" not in st.session_state:
        try:
            with st.spinner("Loading model to memory"):
                st.session_state["qa"] = response_chain(
                    db=st.session_state["chroma_db"], llm=ai_agent()
                )
        except Exception as e:
            st.error(f"Error loading model to memory: {str(e)}")

    # -------------------------------------------------------------------------
    # Load model into memory
    # -------------------------------------------------------------------------
    try:
        if "chroma_db" not in st.session_state:
            with st.spinner("Database Operation. This may take some time..."):
                st.session_state["chroma_db"] = vector_db(
                    hf_embeddings(),
                    load_to_db(st.session_state[absolute_path_to_repo_directory()]),
                )
        if "qa" not in st.session_state:
            st.session_state["qa"] = response_chain(
                db=st.session_state["chroma_db"], llm=ai_agent()
            )
    except Exception as e:
        st.error(f"Error loading model to memory: {str(e)}")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Check if the model has been loaded and is ready to generate responses
    if "qa" in st.session_state:
        # Display the chat interface
        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                if message["content"].startswith("```"):
                    # This message contains a code block
                    code_block = message["content"][3:-3]  # Remove the ``` delimiters
                    language = get_language(
                        code_block
                    )  # Function get_language needs to be defined or imported
                    st.code(code_block, language=language)
                else:
                    st.markdown(message["content"])

        # Get user input and add it to the messages state
        prompt = st.chat_input("Enter your query")
        if prompt:
            st.session_state["messages"].append({"role": "user", "content": prompt})

            # Generate a response using the model
            with st.chat_message("assistant"):
                full_response = ""
                with st.spinner("Generating response..."):
                    result = st.session_state["qa"](prompt)
                full_response += result["answer"]
                time.sleep(0.05)  # This sleep might not be necessary

                if result["answer"].startswith("```"):
                    # The response contains a code block
                    code_block = result["answer"][3:-3]  # Remove the ``` delimiters
                    language = get_language(
                        code_block
                    )  # Function get_language needs to be defined or imported
                    st.code(code_block, language=language)
                else:
                    st.markdown(result["answer"])

                # Update the messages state with the assistant's response
                st.session_state["messages"].append(
                    {"role": "assistant", "content": result["answer"]}
                )


def main():
    streamlit_function()


if __name__ == "__main__":
    main()
