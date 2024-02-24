import streamlit as st
import yaml
import os
import sys
import ast

sys.path.append("../../repochat")

from repochat.constants import (
    absolute_path_to_config,
    configuration,
)


def app():
    config_file = absolute_path_to_config()
    config = configuration()

    # Function to save the updated configuration to the YAML file
    def save_config(updated_config):
        with open(config_file, "w") as file:
            yaml.safe_dump(updated_config, file, default_flow_style=False)

    # Get the current debug value and display the checkbox
    current_debug_value = config["developer"]["debug"]
    new_debug_value = st.checkbox("Debug Mode", value=current_debug_value)

    if new_debug_value != current_debug_value:
        config["developer"]["debug"] = new_debug_value
        save_config(config)

        # Get the current escalation value and display the checkbox
    current_escalate_value = config["models"]["escalation"]
    new_escalate_value = st.checkbox("Enable Escalation", value=current_escalate_value)

    if new_escalate_value != current_escalate_value:
        config["models"]["escalation"] = new_escalate_value
        save_config(config)

    st.divider()
    st.markdown("**Repository**")

    curret_github_url = config["github"]["url"]
    new_github_url = st.text_input("Github Url", value=curret_github_url)
    if new_github_url != curret_github_url:
        config["github"]["url"] = new_github_url
        save_config(config)

    curret_github_branch = config["github"]["branch"]
    new_github_branch = st.text_input("Github Branch", value=curret_github_branch)
    if new_github_branch != curret_github_branch:
        config["github"]["branch"] = new_github_branch
        save_config(config)

    curret_github_username = config["github"]["username"]
    new_github_username = st.text_input("Github Username", value=curret_github_username)
    if new_github_username != curret_github_username:
        config["github"]["username"] = new_github_username
        save_config(config)

    curret_github_token = config["github"]["token"]
    new_github_token = st.text_input("Github Token", value=curret_github_token)
    if new_github_token != curret_github_token:
        config["github"]["token"] = new_github_token
        save_config(config)

    st.divider()
    st.markdown("**OpenRouter**")

    curret_openrouter_api_key = config["keys"]["openrouter"]
    new_openrouter_api_key = st.text_input(
        "OpenRouter API Key", value=curret_openrouter_api_key
    )
    if new_openrouter_api_key != curret_openrouter_api_key:
        config["github"]["url"] = new_openrouter_api_key
        save_config(config)

    st.divider()
    st.markdown("**Allow list of file extensions**")
    st.markdown(""":red[Only files with approved extensions will be kept.]""")
    st.markdown(""":red[All files with extensions not in this list will be deleted.]""")

    current_allowed_extensions = config.get("allowed_file_extensions", [])
    new_allowed_extensions = st.multiselect(
        "Allowed File Extensions",
        options=[
            ".py",
            ".html",
            ".css",
            ".js",
            ".md",
            ".txt",
            ".java",
            ".cpp",
            ".sql",
            ".pdf",
        ],  # Add more options as needed
        default=current_allowed_extensions,
        help="Select allowed file extensions",
    )

    if new_allowed_extensions != current_allowed_extensions:
        config["allowed_file_extensions"] = new_allowed_extensions
        save_config(config)

    st.divider()
    st.markdown("**Delete these paths from the the repository.**")
    st.markdown(
        """:red[Sometimes you have paths in your repo that you do not want to query.]"""
    )
    st.markdown(""":red[This setting will remove those paths after cloning.]""")
    blocked_file_paths = config.get(
        "blocked_file_paths",
        [
            "umqulu/lib",
            "umqulu/workflow/migrations",
            "umqulu/share",
            "umqulu/bin",
            "umqulu/test",
            ".git",
        ],
    )

    # Display current blocked file paths
    with st.container(border=True):
        st.write("Current Blocked File Paths:")
        for path in blocked_file_paths:
            st.text(path)

    # Add a new blocked file path
    new_blocked_path = st.text_input("Add a new blocked file path")
    if st.button("Add"):
        if new_blocked_path and new_blocked_path not in blocked_file_paths:
            blocked_file_paths.append(new_blocked_path)
            config["blocked_file_paths"] = blocked_file_paths
            save_config(config)
            st.success("Blocked file path added successfully.")

    # Remove a blocked file path
    path_to_remove = st.selectbox(
        "Select a blocked file path to remove", options=blocked_file_paths
    )
    if st.button("Remove"):
        if path_to_remove in blocked_file_paths:
            blocked_file_paths.remove(path_to_remove)
            config["blocked_file_paths"] = blocked_file_paths
            save_config(config)
            st.success("Blocked file path removed successfully.")

    st.divider()
    st.markdown("**Always delete these files.**")
    st.markdown(""":red[Danger this will override other settings!]""")
    st.markdown(""":red[All files with extensions in this list will be deleted.]""")
    blocked_files = config.get(
        "blocked_files",
        [
            "__init__.py",
            "README.md",
            ".gitignore",
            ".DS_Store",
            "umqulu.sublime-project",
            "umqulu.sublime-workspace",
            "tools.py",
            "configmaker.py",
        ],
    )

    # Display current blocked files
    with st.container(border=True):
        st.write("Current Blocked Files:")
        for file in blocked_files:
            st.text(file)

    # Add a new blocked file
    new_blocked_file = st.text_input("Add a new blocked file")
    if st.button("Add Blocked File"):
        if new_blocked_file and new_blocked_file not in blocked_files:
            blocked_files.append(new_blocked_file)
            config["blocked_files"] = blocked_files
            save_config(config)
            st.success("Blocked file added successfully.")

    # Remove a blocked file
    file_to_remove = st.selectbox(
        "Select a blocked file to remove", options=blocked_files
    )
    if st.button("Remove Blocked File"):
        if file_to_remove in blocked_files:
            blocked_files.remove(file_to_remove)
            config["blocked_files"] = blocked_files
            save_config(config)
            st.success("Blocked file removed successfully.")

    st.divider()
    st.markdown("**Models.**")
    st.markdown(""":red[Select the model to use!]""")
    st.markdown(""":red[Edit the config file manually to change or add models.]""")
