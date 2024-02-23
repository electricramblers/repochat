from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import MultiQueryRetriever
from typings import List
from pydantic import BaseModel, Field
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser

import streamlit as st

from models import ai_agent

from db import load_code, embedding_chooser, vector_db

from constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
    get_current_time_date,
)


# -------------------------------------------------------------------------------
# Multiple expensive queries
# -------------------------------------------------------------------------------


class multiQueryChain:
    def __init__(self):
        pass

    def model_prompt():
        prompt = hub.pull("defishguy/rag-prompt")
        return prompt

    def get_retriever(self, code):
        llm_to_use = ai_agent()[0]
        vectorstore = vector_db()
        retriever = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(), llm=llm_to_use
        )
        return retriever

    def get_prompt():
        prompt = hub.pull("rlm/rag-prompt")
        return prompt

    def analyze_code(self, code=None):
        if not isinstance(self, multiQueryChain):
            raise TypeError("self is not an instance of multiQueryChain")
        code = load_code()
        # put to vectorstore
        retriever = self.get_retriever(code)
        # create conversation chain
        st.session_state.conversation = self.get_conversation(retriever)
