import os
import re
import shutil
import yaml
import sqlite3
import streamlit as st
from termcolor import colored
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import NotebookLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

from .constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
    get_current_time_date,
)


# ------------------------------------------------------------------------------
# Embedding Stuff
# ------------------------------------------------------------------------------


def hf_embeddings():
    model_to_use = configuration()["models"]["embedding"]
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    return HuggingFaceEmbeddings(
        model_name=model_to_use,
    )


# ------------------------------------------------------------------------------
# Database
# ------------------------------------------------------------------------------


def vector_db():
    config = configuration()
    database_path = absolute_path_to_database_directory()
    repo_path = absolute_path_to_repo_directory()
    code = load_code()
    embeddings = hf_embeddings()
    db_name_only = database_name_only()
    persist_directory = absolute_path_to_database_directory()
    collection_name = "db_collection"
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2048, chunk_overlap=256, length_function=len
    )
    vector_db = Chroma.from_documents(
        documents=code,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory,
    )
    vector_db.persist()
    return vector_db


def load_code():
    repo_path = absolute_path_to_repo_directory()
    code = []
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
                    code.extend(loader.load_and_split())
            except Exception as e:
                pass
    return code
