from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.retrievers import ParentDocumentRetriever
from langchain import globals
import streamlit as st
from .db import load_code, embedding_chooser

from .constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
    get_current_time_date,
)


def prompt_format(system_prompt, instruction):
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<SYS>>\n", "\n<</SYS>>\n\n"
    SYSTEM_PROMPT = B_SYS + system_prompt + E_SYS
    prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
    return prompt_template


def model_prompt():
    system_prompt = """You are a helpful assistant, you have good knowledge in coding and you will use the provided context to answer user questions with detailed explanations.
    Read the given context before answering questions and think step by step. If you can not answer a user question based on the provided context, inform the user. Do not use any other information for answering user"""
    instruction = """
    Context: {context}
    User: {question}"""
    return prompt_format(system_prompt, instruction)


def custom_que_prompt():
    que_system_prompt = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question and give only the standalone question as output in the tags <question> and </question>.
    """

    instr_prompt = """Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""

    return prompt_format(que_system_prompt, instr_prompt)


def response_chain(db, llm):
    globals.set_verbose(True)
    retriever = db.as_retriever()
    search_kwargs = {
        "k": 3,
    }

    retriever.search_kwargs.update(search_kwargs)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    model_template = model_prompt()
    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context", "question"], template=model_template
    )
    question_prompt = PromptTemplate.from_template(custom_que_prompt())

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        chain_type="stuff",
        verbose=globals.get_verbose(),
        combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT},
        condense_question_prompt=question_prompt,
    )

    return qa


# -------------------------------------------------------------------------------
# New stuff below
# -------------------------------------------------------------------------------


def get_retriever(code):
    store = InMemoryStore()
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, chunk_overlap=200, length_function=len
    )
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, length_function=len)
    vectorstore = Chroma(
        collection_name="db_collection", embedding_function=embedding_chooser()
    )
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    retriever.add_documents(code, ids=None)
    return retriever


def get_prompt():
    template = (
        "Combine the chat history and follow up question into "
        f"a standalone question. The date and time is {get_current_time_date()}. Chat History: {chat_history}"
        "Follow up question: {question}"
    )
    prompt = PromptTemplate.from_template(template)
    question_generator_chain = LLMChain(llm=st.session_state.llm, prompt=prompt)


def get_conversation(retriever):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=st.session_state.llm, retriever=retriever, memory=memory
    )
    return conversation_chain


def analyze_code(code):  # removed the code argument
    # put to vectorstore
    retriever = get_retriever(code)
    # create conversation chain
    st.session_state.conversation = get_conversation(retriever)
