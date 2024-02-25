#!/usr/bin/env python

import os
from termcolor import colored
from repochat.constants import (
    absolute_path_to_config,
    configuration,
    absolute_path_to_repo_directory,
    absolute_path_to_database_directory,
)

# List of files to include
files = [
    "app.py",
    "altPages/index.py",
    "multipage.py",
    "repochat/multiQueryChain.py",
    "repochat/db.py",
]

ADDED_TEXT = """The code from multiple files is present in this prompt.  Each file name looks like "# <something>.py"

Be exceptionally cautious to preserve code, there is a reason the code is there even if you are fixing problems. \n\nHERE IS THE PROBLEM:\n\n\n\nIt is very important that you carefully follow instuctions.  Step by step, slowly go through the code to solve the problem."""

# Create the output file
with open("prompt.txt", "w") as outfile:
    # Write the ADDED_TEXT content at the beginning of the file
    outfile.write(ADDED_TEXT + "\n\n")

    # Iterate through each file
    for filename in files:
        print(colored(f"Helper ingesting: {filename}\n", "cyan"))
        # Check if the file exists in the current directory or any subdirectories
        if any(
            os.path.isfile(os.path.join(root, filename)) for root, _, _ in os.walk(".")
        ):
            # Get the full path of the file
            filepath = next(
                os.path.join(root, filename)
                for root, _, _ in os.walk(".")
                if os.path.isfile(os.path.join(root, filename))
            )

            # Open the file and read its contents
            with open(filepath, "r") as infile:
                file_contents = infile.read()

                # Remove trailing whitespace and carriage returns
                file_contents = file_contents.rstrip()

            # Write a comment indicating the file name
            outfile.write(f"\n\n# {filename}\n")

            # Write the file contents
            outfile.write(file_contents)
        else:
            print(f"Error: {filename} not found")

print(colored("Finished", "yellow"))

print(
    colored(
        f"The absolute path to the config is: {absolute_path_to_config()}", "magenta"
    )
)
print(
    colored(
        f"The absolute path to the repository is: {absolute_path_to_repo_directory()}",
        "magenta",
    )
)
print(
    colored(
        f"The absolute path to the database is: {absolute_path_to_database_directory()}",
        "magenta",
    )
)
