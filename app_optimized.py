import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import Chroma
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template

def init():
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None        
    if "llm" not in st.session_state:
        st.session_state.llm = ChatOpenAI(temperature=0, model_name='gpt-4')
    if "embeddings" not in st.session_state:
        st.session_state.embeddings = OpenAIEmbeddings()    
        #st.session_state.embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    
def load_pdfs_from_directory(directory):
    loaded_pdfs = []
    # Durchlaufen aller Dateien im Verzeichnis
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            # Verwenden des PyPDFLoaders, um das PDF-Dokument einzulesen
            pdf_loader = PyPDFLoader(file_path)
            #document = pdf_loader.load()
            #loaded_pdfs.append((filename, document))
            pages = pdf_loader.load_and_split()
            loaded_pdfs.append((filename, pages))
    return loaded_pdfs

def get_pdf_text(pdf_docs):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    samples_directory = os.path.join(current_directory, "samples")

    pdf_docs=load_pdfs_from_directory(samples_directory)
    all_pages=[]
    for filename,pages in pdf_docs:
        all_pages.extend(pages)
    st.write(all_pages)
    return all_pages

def get_retriever(pages):
    store = InMemoryStore()
    parent_splitter=RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=200, length_function=len)
    child_splitter=RecursiveCharacterTextSplitter(chunk_size=400, length_function=len)
    vectorstore = Chroma(collection_name="split_parents", embedding_function=OpenAIEmbeddings())
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter
    )
    retriever.add_documents(pages, ids=None)
    return retriever

def get_prompt():
    template = (
        "Combine the chat history and follow up question into "
        "a standalone question. Chat History: {chat_history}"
        "Follow up question: {question}"
    )
    prompt = PromptTemplate.from_template(template)
    question_generator_chain = LLMChain(llm=st.session_state.llm, prompt=prompt)


def get_conversation(retriever):
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)  
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=st.session_state.llm,
        retriever=retriever,
        memory = memory    
    )
    return conversation_chain

chain = ConversationalRetrievalChain(
    combine_docs_chain=combine_docs_chain,
    retriever=retriever,
    question_generator=question_generator_chain,
)



def analyze_documents(pdf_docs):
    #get pdf text
    pages = get_pdf_text(pdf_docs)
    #put to vectorstore
    retriever = get_retriever(pages)
    #create conversation chain
    st.session_state.conversation = get_conversation(retriever) 

def handle_user_input(question):
    response = st.session_state.conversation({'question':question})
    st .session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            with st.chat_message("user"):
                st.write(message.content)
#            st.write(user_template.replace(
#                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            with st.chat_message("assistant"):
                st.write(message.content)
#           st.write(bot_template.replace(
#                "{{MSG}}", message.content), unsafe_allow_html=True)

def main():
    load_dotenv()
    init()

    st.set_page_config(page_title="Förderrichtlinien-Assistent", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    st.header(":books: Förderrichtlinien-Assistent ")
    user_input = st.chat_input("Stellen Sie Ihre Frage hier")
    if user_input:
        with st.spinner("Führe Anfrage aus ..."):
            handle_user_input(user_input)


    with st.sidebar:
        st.subheader("Förderrichtlinien")
        pdf_docs=st.file_uploader("Dokumente hier hochladen", accept_multiple_files=True)
        if st.button("Hochladen"):
            with st.spinner("Analysiere Dokumente ..."):
                analyze_documents(pdf_docs)

        #st.write('<div style="position: fixed;bottom:16px;left:16px;"><a href="https://www.flaticon.com/free-icons/bot" title="bot icons">Bot icons created by Freepik - Flaticon</a></div>',unsafe_allow_html=True)


if __name__ == "__main__":
    main()