#!/usr/bin/env python
import os
import yaml
from termcolor import colored
from langchain_community.embeddings import (
    HuggingFaceEmbeddings,
    OpenAIEmbeddings,
)
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain

from constants import absolute_path_to_repo_directory, configuration

config = configuration()


def find_files():
    directory = absolute_path_to_repo_directory()
    docs = []  # Initialize an empty list to store file paths
    for root, dirs, files in os.walk(directory):
        for file in files:
            docs.append(os.path.join(root, file))  # Add the file path to the list
    return docs


docs = find_files()
parent_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.MARKDOWN,
    chunk_size=400,
    chunk_overlap=40,
)

child_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.MARKDOWN,
    chunk_size=100,
    chunk_overlap=10,
)

vectorstore = Chroma()

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
retriever = ParentDocumentRetriever(vectorstore=vectorstore, embeddings=embeddings)

retriever.add_documents(docs)

retrieval_chain = ConversationalRetrievalChain()
retrieval_chain.add_retriever(retriever)

OpenAIEmbeddings.set_api_key("YOUR_OPENAI_API_KEY")


def chat_client():
    while True:
        user_input = input("User: ")
        response = retrieval_chain.get_response(user_input)
        print("Bot:", response)


if __name__ == "__main__":
    chat_client()
