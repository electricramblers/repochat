---
"""
This is an example of what the config.yaml file looks like.  It is saved here with the md file extension to keep it from being read by the application
"""

blocked_file_paths:
  - directory/next_directory/lib
  - directory/next_directory/migrations
  - directory/next_directory/share
  - directory/next_directory/bin
  - directory/next_directory/test
  - .git

allowed_file_extensions:
  - .py
  - .html
  - .css
  - .js
  - .md

blocked_files:
  - '__init__.py'
  - 'README.md'
  - '.gitignore'
  - '.DS_Store'

github:
  url: https://github.com/electricramblers/fizzbuzz
  token: <sanitized>
  branch: main
  username: <username>

models:
  escalation: False
  ollama:
    local: dolphin-mistral:v2.6
    remote: dolphin-mistral:v2.6
    base_url: http://imac:11434
  openrouter:
    low: openchat/openchat-7b:free
    medium: google/gemini-pro
    high: mistralai/mistral-medium
  embedding: sentence-transformers/all-mpnet-base-v2
  
llm_order:
  - local
  - remote
  - external

keys:
  openrouter: <sanitized>

hideme: PHxpbV9lbmR8Pg==
