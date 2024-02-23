from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import MultiQueryRetriever
from langchain_community.vectorstores import Chroma

# from typings import List
from pydantic import BaseModel, Field
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser

from termcolor import colored
import streamlit as st

from .models import ai_agent

from .db import load_code, embedding_chooser, vector_db

from .constants import (
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


class multiQueryChainClass:
    def __init__(self):
        pass

    def model_prompt(self):
        from langchain import hub

        if configuration()["developer"]["debug"]:
            print(colored(f"multiQueryChainClass.model_prompt invoked\n", "magenta"))
        return hub.pull("defishguy/rag-prompt")

    def get_retriever(self):
        llm_to_use = ai_agent()[0]
        embeddings = embedding_chooser()
        db_path = absolute_path_to_database_directory()
        database_store = vector_db()
        # Load the existing vector database
        try:
            vectorstore = database_store
        except Exception as e:
            print(colored(f"line 54 - multiQueryChainClass.get_retriever: {e}", "red"))
        try:
            retriever = MultiQueryRetriever.from_llm(
                retriever=vectorstore.as_retriever(), llm=llm_to_use
            )
        except Exception as e:
            print(colored(f"line 60 - multiQueryChainClass.get_retriever: {e}", "red"))
        if configuration()["developer"]["debug"]:
            print(
                colored(
                    f"line 63 - multiQueryChainClass.get_retriever invoked\n", "magenta"
                )
            )
        return retriever

    def get_conversation(self, retriever):
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=st.session_state.llm,
            retriever=retriever,
            memory=memory,
        )
        if configuration()["developer"]["debug"]:
            print(
                colored(
                    f"line 80 -multiQueryChainClass.get_conversation invoked\n",
                    "magenta",
                )
            )
        return conversation_chain

    def analyze_code(self):
        if not isinstance(self, multiQueryChainClass):
            raise TypeError(
                colored("self is not an instance of multiQueryChainClass", "red")
            )
        # get retriever
        retriever = self.get_retriever()
        # create conversation chain
        if configuration()["developer"]["debug"]:
            print(
                colored(
                    f"line 90 - multiQueryChainClass.analyze_code invoked\n", "magenta"
                )
            )
        st.session_state.conversation = self.get_conversation(retriever)
