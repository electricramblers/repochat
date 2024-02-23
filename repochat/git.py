import os
import json
import re
import time
import shutil
from git import Repo
from git.exc import GitCommandError

import requests
import urllib3

from termcolor import colored
from .utils import pruner

from .constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
    get_current_time_date,
)


def post_clone_actions():
    pruner()


def clone_repository():
    """
    Clones a Git repository to the specified directory.

    Args:
        None

    Returns:
        None

    Raises:
        requests.exceptions.HTTPError: If the repository is private and the authentication credentials are invalid.
        GitError: If there is an error cloning the repository.
    """
    config = configuration()
    git_url = config["github"]["url"]
    repo_dir = absolute_path_to_repo_directory()
    username = config["github"]["username"]
    password = config["github"]["token"]
    branch = config["github"]["branch"]

    try:
        shutil.rmtree(repo_dir)
        time.sleep(2)
    except Exception as e:
        print(colored(f"Error removing repository directory: {e}", "red"))

    try:
        shutil.rmtree(absolute_path_to_database_directory())
        time.sleep(2)
    except Exception as e:
        print(colored(f"Error removing the database directory: {e}", "red"))

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
