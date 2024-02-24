from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.vectorstores import Chroma
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks.manager import CallbackManager, CallbackManagerForLLMRun
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from typing import List
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
# Parsing stuff
# -------------------------------------------------------------------------------


class LineList(BaseModel):
    # "lines" is the key (attribute name) of the parsed output
    lines: List[str] = Field(description="Lines of text")


class LineListOutputParser(PydanticOutputParser):
    def __init__(self) -> None:
        super().__init__(pydantic_object=LineList)

    def parse(self, text: str) -> LineList:
        lines = text.strip().split("\n")
        return LineList(lines=lines)


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
        return conversation_chain

    def get_retriever(self, code):
        retriever = MultiQueryRetriever.from_llm(
            retriever=self.db.as_retriever(), llm=self.llm
        )
        return retriever

    def get_rag(self, question):
        # Retrieve documents based on the question
        mqRetriever = self.get_retriever(question)

        # Assuming mqRetriever retrieves documents and we need to format them
        # Here, we simulate retrieving and formatting documents
        documents = mqRetriever.retrieve(
            question
        )  # This line is pseudo-code; replace with actual retrieval call

        # Building the RAG chain
        rag_chain = {
            "context": "\n\n".join(doc.page_content for doc in documents),
            "question": question,
        }

        # Process the RAG chain
        # Assuming 'prompt', 'llm', and 'StrOutputParser' are methods or functions that process the input
        formatted_input = self.prompt(rag_chain)
        llm_output = self.llm(formatted_input)
        result = StrOutputParser().parse(
            llm_output
        )  # Assuming StrOutputParser has a parse method

        return result

    def question_and_answer(self, question):
        retriever = self.get_retriever(code)
        st.session_state.conversation = self.get_rag(question)
