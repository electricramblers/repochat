import os
import re
import shutil
import subprocess
import streamlit as st

from termcolor import colored

from .constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
)


def pruner():
    config = configuration()
    parent_directory = absolute_path_to_repo_directory()
    blocked_file_paths = config.get("blocked_file_paths", [])
    allowed_file_extensions = config.get("allowed_file_extensions", [])
    blocked_files = config.get("blocked_files", [])

    print(
        colored(
            f"Deleting files based on blocked file paths: {blocked_file_paths}", "cyan"
        )
    )
    for path in blocked_file_paths:
        file_path = os.path.join(parent_directory, path)
        if os.path.exists(file_path):
            print(colored(f"Deleting {file_path}", "yellow"))
            shutil.rmtree(file_path)
        else:
            print(colored(f"{file_path} does not exist", "blue"))

    # Get all possible file extensions
    all_extensions = set(
        os.path.splitext(f)[1]
        for f in os.listdir(parent_directory)
        if os.path.isfile(os.path.join(parent_directory, f))
    )
    all_extensions.discard("")

    # Get disallowed file extensions
    disallowed_extensions = all_extensions - set(allowed_file_extensions)

    print(
        colored(
            f"Deleting files based on disallowed file extensions: {disallowed_extensions}",
            "cyan",
        )
    )

    def delete_disallowed_files():
        directory = absolute_path_to_repo_directory()
        files_to_delete = [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
        allowed_extensions = set(config["allowed_file_extensions"])
        files_to_keep = []
        for file in files_to_delete:
            _, ext = os.path.splitext(file)
            if ext in allowed_extensions:
                files_to_keep.append(file)
        files_to_delete = set(files_to_delete) - set(files_to_keep)
        for file in files_to_delete:
            print(colored(f"Deleting {file}", "yellow"))
            os.remove(os.path.join(directory, file))

    delete_disallowed_files()

    print(colored(f"Deleting blocked files: {blocked_files}", "cyan"))
    for file in blocked_files:
        file_path = os.path.join(parent_directory, file)
        if os.path.exists(file_path):
            print(colored(f"Deleting {file_path}", "yellow"))
            os.remove(file_path)
        else:
            print(colored(f"{file_path} does not exist", "blue"))


def check_git_url(url):
    print(colored(f"This is the url I am checking: {url}", "green"))
    # Try to clone the repository using GitPython
    try:
        Repo.clone_from(url, "/tmp/test_repo")
        # If cloning succeeds, the URL exists and is public
        return {"exists": True, "public": True}
    except Exception as e:
        pass

    # If cloning fails, try to make a HEAD request to the URL
    git_url = url.replace("https://", "https://")
    response = requests.head(git_url, timeout=5, allow_redirects=True)

    # If the HEAD request is successful and the response code is 2xx, the URL exists and is public
    if response.status_code // 100 == 2:
        return {"exists": True, "public": True}

    # If the HEAD request is successful and the response code is 401, the URL exists and is private
    elif response.status_code == 401:
        return {"exists": True, "public": False}

    # If the HEAD request fails or returns any other response code, the URL does not exist
    else:
        return {"exists": False, "public": None}
