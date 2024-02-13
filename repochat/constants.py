import os
import yaml
import re
from termcolor import colored


def absolute_path_to_config():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    config_path = os.path.join(parent_dir, "config.yaml")
    return config_path


def configuration():
    confg_file = absolute_path_to_config()
    with open(confg_file, "r") as file:
        cfg = yaml.safe_load(file)
    return cfg


def absolute_path_to_repo_directory():
    config = configuration()
    url_to_breakdown = config["github"]["url"]
    match = re.search(r"github\.com/([^/]+)/([^/]+)", url_to_breakdown)
    if match:
        a = match.group(1)
        b = match.group(2)
    else:
        raise ValueError("Invalid GitHub URL")
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    repository_path = os.path.join(parent_dir, f"repo_{a}_{b}")
    return repository_path


def absolute_path_to_database_directory():
    config = configuration()
    url_to_breakdown = config["github"]["url"]
    match = re.search(r"github\.com/([^/]+)/([^/]+)", url_to_breakdown)
    if match:
        a = match.group(1)
        b = match.group(2)
    else:
        raise ValueError("Invalid GitHub URL")
    current_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    database_path = os.path.join(parent_dir, f"database_{a}_{b}")
    return database_path
