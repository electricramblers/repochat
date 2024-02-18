from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain


def response_chain(db, llm):
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
        verbose=True,
        combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT},
        condense_question_prompt=question_prompt,
    )

    return qa


def prompt_format(system_prompt, instruction):
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<SYS>>\n", "\n<</SYS>>\n\n"
    SYSTEM_PROMPT = B_SYS + system_prompt + E_SYS
    prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
    return prompt_template


def model_prompt():
    system_prompt = """You are a helpful assistant, you have good knowledge in coding and you will use the provided context to answer user questions with detailed explanations.  Always consider policies and summaries in markdown files.
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
