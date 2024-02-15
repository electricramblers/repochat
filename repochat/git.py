import requests
import streamlit as st
import uuid
import os
import re
import shutil
from git import Repo
from git.exc import GitCommandError
from termcolor import colored
from .utils import url_name, clone_repo, pruner

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


def refresh_repository():
    repo_path = absolute_path_to_repo_directory()
    database_path = absolute_path_to_database_directory()
    try:
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        if os.path.exists(database_path):
            shutil.rmtree(database_path)
    except PermissionError:
        st.error(
            "Failed to delete the repository and database folders. Please check the folder permissions."
        )
        return
    st.session_state["db_loaded"] = False
    st.session_state["refresh_message"] = True


def git_form(repo_path):
    config = configuration()
    git_url = config["github"]["url"]
    type_repository_answer = check_git_url(git_url)
    print(colored(f"Repo info: {type_repository_answer}", "yellow"))

    # Check if the repository already exists
    if os.path.exists(repo_path):
        warning_message = """
        ⚠️ Warning: Repository already exists!

        Please click the 'Delete Repository' button in the sidebar and then hit dismiss.
        This will remove the existing repository and allow you to clone a new one.
        """
        st.markdown(warning_message, unsafe_allow_html=True)

    for k, v in type_repository_answer.items():
        if not k:
            print(colored(f"The repository does not exist: {k}", "red"))
        elif k and v:
            print(colored("The repository exists and is public.", "cyan"))
            output = public_git_form(repo_path)
            if output is None:
                continue
            return output
        elif k and not v:
            print(colored("The yaml repository exists and is private", "cyan"))
            output = private_git_form(repo_path)
            if output is None:
                continue
            return output
            exit()

    if "refresh_git" in st.session_state:
        refresh_repository()
        return None, None


def private_git_form(repo_path):
    print(colored("private_git_form has loaded", "magenta"))
    config = configuration()
    default_branch = config["github"]["branch"]
    with st.sidebar:
        st.title("GitHub Link")
        with st.form("git"):
            git_url = st.text_input(
                "Enter GitHub Repository Link", value=configuration()["github"]["url"]
            )
            git_branch = st.text_input(
                "Enter GitHub Repository Branch", value=default_branch
            )
            git_token = st.text_input(
                "Enter GitHub Personal Access Token",
                value=configuration()["github"]["token"],
            )
            submit_git = st.form_submit_button("Submit")

    if submit_git:
        with st.spinner("Checking GitHub URL"):
            if not git_url:
                st.warning("Enter GitHub URL")
                return None, None
            try:
                # Extract the owner and repo from the URL
                match = re.match(r"https://github.com/([^/]+)/([^/]+)", git_url)
                if match:
                    owner, repo = match.groups()
                else:
                    st.error("Invalid GitHub URL")
                    return None, None

                # Use the GitHub API to check if the repository exists and is accessible
                api_url = f"https://api.github.com/repos/{owner}/{repo}"
                response = requests.get(
                    api_url, headers={"Authorization": f"token {git_token}"}
                )
                if response.status_code == 200:
                    st.success("GitHub Link loaded successfully!")
                    db_name = url_name(git_url)
                else:
                    st.error("Enter Valid GitHub Repo")
                    return None, None
            except requests.exceptions.MissingSchema:
                st.error("Invalid URL. Please include the scheme (e.g., https://)")
                return None, None

        with st.spinner(f"Cloning {db_name} Repository"):
            try:
                Repo.clone_from(
                    git_url,
                    repo_path,
                    branch=git_branch,
                    env={"GIT_ASKPASS": "echo", "GIT_USERNAME": git_token},
                )
                st.success("Cloned successfully!")
            except GitCommandError as e:
                st.error(f"Error cloning repository: {e}")
                st.error("Please check the branch name and try again.")
                return None, None

        post_clone_actions()
        return db_name, 1

    return None, None


def public_git_form(repo_path):
    print(colored("public_git_form has loaded", "magenta"))
    config = configuration()
    default_branch = config["github"]["branch"]

    with st.sidebar:
        st.title("GitHub Link")
        with st.form("git"):
            git_url = st.text_input(
                "Enter GitHub Repository Link", value=configuration()["github"]["url"]
            )
            git_branch = st.text_input(
                "Enter GitHub Repository Branch", value=default_branch
            )
            submit_git = st.form_submit_button("Submit")

    if submit_git:
        with st.spinner("Checking GitHub URL"):
            if not git_url:
                st.warning("Enter GitHub URL")
                return None, None
            try:
                response = requests.get(git_url)
                if response.status_code == 200:  # and url_name(git_url):
                    st.success("GitHub Link loaded successfully!")
                    db_name = url_name(git_url)
                else:
                    st.error("Enter Valid GitHub Repo")
                    return None, None
            except requests.exceptions.MissingSchema:
                st.error("Invalid URL. Please include the scheme (e.g., https://)")
                return None, None

        with st.spinner(f"Cloning {db_name} Repository"):
            try:
                Repo.clone_from(git_url, repo_path, branch=git_branch)
                st.success("Cloned successfully!")
            except GitCommandError as e:
                st.error(f"Error cloning repository: {e}")
                st.error("Please check the branch name and try again.")
                return None, None

        post_clone_actions()
        return db_name, 1

    return None, None


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
