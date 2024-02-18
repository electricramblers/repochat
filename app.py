import git
import requests
import os
from termcolor import colored

from repochat.git import clone_repository, post_clone_actions


def main():
    clone_repository()
    post_clone_actions()


if __name__ == "__main__":
    main()
