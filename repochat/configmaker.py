import yaml
import os

from repochat.constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
    repository_name_only,
    database_name_only,
)


def create_yaml_file():
    filename = absolute_path_to_config()
    # Define the data structure for the YAML content
    data = {
        "blocked_file_paths": ["example/path/1", "example/path/2"],
        "allowed_file_extensions": [".py", ".html", ".css", ".js", ".md"],
        "blocked_files": [
            "__init__.py",
            "README.md",
            ".gitignore",
            ".DS_Store",
            "example.sublime-project",
            "example.sublime-workpace",
        ],
        "github": {
            "url": "< your github url >",
            "token": "<your token here>",
            "branch": "main",
            "username": "<your github user name>",
        },
        "models": {
            "escalation": True,
            "ollama": {
                "local": "dolphin-mistral:v2.6",
                "remote": "dolphin-mistral:v2.6",
                "base_url": "<network ollama like this http://ip-address:11434>",
            },
            "openrouter": {
                "low": "openchat/openchat-7b:free",
                "medium": "google/gemini-pro",
                "high": "mistralai/mistral-medium",
                "supervisor": "openai/gpt-4-turbo-preview",
            },
            "embedding": {
                "huggingface": {
                    "model": "sentence-transformers/all-mpnet-base-v2",
                    "use": True,
                }
            },
        },
        "keys": {"openrouter": "<your api-key goes here>"},
    }

    with open(os.path.join(filename), "w") as file:
        yaml.dump(data, file, default_flow_style=False)
