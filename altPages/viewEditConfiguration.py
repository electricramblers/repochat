import streamlit as st
import yaml
import os
import sys

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

    # Check if the debug value has changed
    if new_debug_value != current_debug_value:
        # Update the debug value in the configuration
        config["developer"]["debug"] = new_debug_value
        # Save the updated configuration
        save_config(config)
