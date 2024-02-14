import requests
import streamlit as st
import uuid
from git import Repo
from termcolor import colored
from .utils import url_name, clone_repo

from .constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
)


def git_form(repo_path):
    config = configuration()
    git_url = config["github"]["url"]
    type_repository_answer = check_git_url(git_url)
    print(colored(f"Repo info: {type_repository_answer}", "yellow"))
    for k, v in type_repository_answer.items():
        if not k:
            print(colored(f"The yaml repository does not exist: {k}", "red"))
        elif k and v:
            print(colored("The yaml repository exists and is public.", "cyan"))
            output = public_git_form(repo_path)
            return output
        elif k and not v:
            print(colored("The yaml reposistory exists and is private", "cyan"))
            exit()


def public_git_form(repo_path):
    config = configuration()
    print(colored(f"I am executing public_git_form({repo_path})", "cyan"))
    with st.sidebar:
        st.title("GitHub Link")
        with st.form("git"):
            git_url = st.text_input(
                "Enter GitHub Repository Link", value=configuration()["github"]["url"]
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
                    # db_name = database_name_only()
                else:
                    st.error("Enter Valid GitHub Repo")
                    return None, None
            except requests.exceptions.MissingSchema:
                st.error("Invalid URL. Please include the scheme (e.g., https://)")
                return None, None

        with st.spinner(f"Cloning {db_name} Repository"):
            clone_repo(git_url, repo_path)
            st.success("Cloned successfully!")
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
