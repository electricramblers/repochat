import os
import shutil
import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import NotebookLoader, TextLoader
from .constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
)


def vector_db(embeddings, code):
    persist_directory = absolute_path_to_database_directory()
    collection_name = "db_collection"
    vec_db = Chroma.from_documents(
        documents=code,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory,
    )
    vec_db.persist()
    return vec_db


def load_to_db(repo_path):
    docs = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for filename in files:
            if filename.startswith("."):
                continue
            if filename == "package-lock.json":
                continue
            file_path = os.path.join(root, filename)
            try:
                if file_path.endswith(".ipynb"):
                    loader = NotebookLoader(file_path)
                else:
                    loader = TextLoader(file_path, encoding="utf-8")
                    docs.extend(loader.load_and_split())
            except Exception as e:
                pass

    code_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    code = code_splitter.split_documents(docs)
    return code
