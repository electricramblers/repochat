import os
import json
import re
import shutil
from git import Repo
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
)


def post_clone_actions():
    print(colored("Running post-clone actions", "magenta"))
    pruner()


def clone_repository():
    """
    Clones a Git repository to the specified directory.

    Args:
        git_url (str): The URL of the Git repository to clone.
        repo_dir (str): The directory to clone the repository into.
        username (str, optional): The username to use when authenticating to a private repository.
        password (str, optional): The password to use when authenticating to a private repository.

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
        shutil.rmtree(absolute_path_to_repo_directory())
        print(colored("Removing existing repository.", "cyan"))
    except:
        pass
    try:
        shutil.rmtree(absolute_path_to_database_directory())
        print(colored("Removing existing database directory.", "cyan"))
    except:
        pass
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
        Repo.clone_from(git_url, repo_dir)
        print(colored("Cloning complete.", "cyan"))
    except Exception as e:
        raise GitError(f"Error cloning repository: {e}") from e
