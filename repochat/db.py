import os
import shutil
import yaml
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
)


# ------------------------------------------------------------------------------
# Embedding Chooser
# ------------------------------------------------------------------------------


def get_first_true_embedding():
    config = configuration()
    true_embeddings = [k for k, v in config["models"]["embedding"].items() if v["use"]]
    if len(true_embeddings) == 0:
        raise ValueError("No 'use: true' embeddings found")
    elif len(true_embeddings) > 1:
        raise ValueError("Multiple 'use: true' embeddings found")
    else:
        return (
            true_embeddings[0],
            config["models"]["embedding"][true_embeddings[0]]["model"],
        )


def embedding_chooser():
    config = configuration()
    try:
        embedding_key, embedding_config = get_first_true_embedding()
        match embedding_key:
            case "huggingface":
                os.environ["TOKENIZERS_PARALLELISM"] = "false"
                print(colored(f"Embedding: {embedding_config}", "yellow"))
                return HuggingFaceEmbeddings(model_name=embedding_config)
        match embedding_key:
            case "voyageai":
                return
    except Exception as e:
        print(colored(f"Error at embedding_chooser(): {e}", "cyan"))
        # Handle the error appropriately, perhaps re-raise or return None
        raise


# ------------------------------------------------------------------------------
# Database
# ------------------------------------------------------------------------------


def load_code():
    repo_path = absolute_path_to_repo_directory()
    print(colored("line 64 in db.py - Loading Documents", "cyan"))
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
    return code
