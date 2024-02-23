from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import MultiQueryRetriever
from langchain_community.vectorstores import Chroma

# from typings import List
from pydantic import BaseModel, Field
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain import hub

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


class multiQuery:
    """
    A class to handle multiple queries with a retriever from a persistent database.

    Attributes:
        llm: An instance of a language model.
        prompt: A prompt object for generating queries.
        persist_dir: The absolute path to the database directory.
        db: A Chroma database instance.
        retriever: A retriever object to fetch data from the database.

    Methods:
        get_conversation(retriever): Creates a conversation chain using the provided retriever.
        run_rag_lcel(): Runs a retrieval-augmented generation chain and returns the result.

    Usage:
        # Initialize the multiQuery class
        mq = multiQuery()

        # Access the retriever attribute
        retriever_instance = mq.retriever

        # Use the get_conversation method with the retriever
        conversation_chain = mq.get_conversation(retriever_instance)

        # Run the retrieval-augmented generation chain
        result = mq.get_rag()
    """

    def __init__(self):
        self.database_name = f"db_{database_name_only()}"
        self.llm = ai_agent()[0]
        self.prompt = hub.pull("defishguy/rag-prompt")
        self.persist_dir = absolute_path_to_database_directory()
        self.db = vector_db()
        self.retriever = self.db.as_retriever()

    def get_conversation(self, retriever):
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
        )
        # Debug print to check if the retriever is fetching any documents
        print(f"Retrieved documents: {retriever.retrieve()}")
        # Debug print to check if the documents have any content
        print(f"Document content: {retriever.retrieve().page_content}")
        return conversation_chain

    def get_rag(self):
        rag_chain = (
            {
                "context": self.retriever
                | (lambda docs: "\n\n".join(doc.page_content for doc in docs)),
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        return rag_chain

    def analyze_code(self, code=None):
        retriever = self.retriever
        st.session_state.conversation = self.get_conversation(retriever)
