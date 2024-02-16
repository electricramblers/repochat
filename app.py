import time
import streamlit as st

from repochat.utils import init_session_state
from repochat.git import git_form, refresh_repository
from repochat.db import vector_db, load_to_db
from repochat.models import hf_embeddings, ai_agent
from repochat.chain import response_chain
from repochat.constants import REFRESH_MESSAGE


init_session_state()

st.set_page_config(
    page_title="SprocketSorcerer, the Automaton Archduke of Articulation",
    page_icon="💻",
    initial_sidebar_state="expanded",
    menu_items={
        "Report a bug": "https://github.com/electricramblers/repochat/issues",
        "About": "Do or do not. There is no try. -Yoda",
    },
)

st.markdown(
    "<h1 style='text-align: center;'>SprocketSorcerer\nThe Automaton Archduke of Articulation</h1>",
    unsafe_allow_html=True,
)

try:
    if not st.session_state["db_loaded"]:
        st.session_state["db_name"], st.session_state["git_form"] = git_form(
            st.session_state["repo_path"]
        )

    if st.session_state["git_form"]:
        with st.spinner("Loading the contents to database. This may take some time..."):
            st.session_state["chroma_db"] = vector_db(
                hf_embeddings(), load_to_db(st.session_state["repo_path"])
            )
        with st.spinner("Loading model to memory"):
            st.session_state["qa"] = response_chain(
                db=st.session_state["chroma_db"], llm=ai_agent()
            )

        st.session_state["db_loaded"] = True
except TypeError:
    pass

# Add a Streamlit button for refreshing the repository only in the sidebar
with st.sidebar:
    if st.button("Delete Repository"):
        refresh_repository()
        st.session_state["db_loaded"] = False
        st.rerun()

    # Display the refresh message only in the sidebar
    if st.session_state.get("refresh_message", False):
        st.warning(REFRESH_MESSAGE)
        st.session_state["refresh_message"] = False


if st.session_state["db_loaded"]:
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            if message["content"].startswith("```"):
                # This message contains a code block
                code_block = message["content"][3:-3]  # Remove the ``` delimiters
                language = get_language(
                    code_block
                )  # Assuming a function get_language exists
                st.code(code_block, language=language)
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("Enter your query"):
        st.session_state["messages"].append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            full_response = ""
            with st.spinner("Generating response..."):
                result = st.session_state["qa"](prompt)
            full_response += result["answer"]
            time.sleep(0.05)  # This sleep might not be necessary anymore

            if result["answer"].startswith("```"):
                # The response contains a code block
                code_block = result["answer"][3:-3]  # Remove the ``` delimiters
                language = get_language(
                    code_block
                )  # Assuming a function get_language exists
                st.code(code_block, language=language)
            else:
                st.markdown(result["answer"])

        # Update the messages state with the assistant's response
        st.session_state["messages"].append(
            {"role": "assistant", "content": result["answer"]}
        )
