import os
import json
import re
import time
import shutil
import random
import tempfile
from git import Repo
from git.exc import GitCommandError

import requests
import urllib3

from termcolor import colored
from .utils import pruner

from .constants import (
    RANDOMNUMBER,
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
    get_current_time_date,
)


def pre_clone_actions():
    filename = RANDOMNUMBER
    if configuration()["developer"]["debug"]:
        print(
            colored(
                f"The tempfile name is: pre_clone_actions_lock_{filename}.tmp\n",
                "magenta",
            )
        )
    temp_dir = tempfile.gettempdir()
    lock_file_path = os.path.join(temp_dir, f"pre_clone_actions_lock_{filename}.tmp")
    repo_dir = absolute_path_to_repo_directory()
    if not os.path.exists(lock_file_path):
        if configuration()["developer"]["debug"]:
            print(
                colored(
                    "line 33 git.py - pre_clone_actions has been invoked.\n", "magenta"
                )
            )
        try:
            shutil.rmtree(repo_dir)
            time.sleep(2)
        except Exception as e:
            # print(colored(f"Error removing repository directory: {e}", "red"))
            pass
        try:
            shutil.rmtree(absolute_path_to_database_directory())
            time.sleep(2)
        except Exception as e:
            # print(colored(f"Error removing the database directory: {e}", "red"))
            pass
        with open(lock_file_path, "w") as lock_file:
            lock_file.write(
                "This is a lock file to prevent multiple executions of pre_clone_actions in the same session."
            )
    else:
        print(
            colored(
                "pre_clone_actions() has already been executed in this session.", "cyan"
            )
        )


def post_clone_actions():
    pruner()


def clone_repository():
    config = configuration()
    git_url = config["github"]["url"]
    repo_dir = absolute_path_to_repo_directory()
    username = config["github"]["username"]
    password = config["github"]["token"]
    branch = config["github"]["branch"]

    # Test if the repository is public or private
    response = requests.head(git_url, allow_redirects=True)
    if response.status_code == 403:
        # Repository is private
        if username is None or password is None:
            raise ValueError(
                "Private repository specified but no authentication credentials provided"
            )
        git_url = (
            f"https://{username}:{password}@github.com{git_url.split('github.com')[1]}"
        )

    try:
        repo = Repo.clone_from(git_url, repo_dir)
        repo.git.checkout(branch)
        time.sleep(1)
        return True
    except Exception as e:
        print(colored(f"Error cloning repository: {e}", "red"))
        return False
