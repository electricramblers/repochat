# index.py
import streamlit as st
import os
import sys
from termcolor import colored, cprint

sys.path.append("../../repochat")

from repochat.multiQueryChain import multiQuery


# Initialize the multiQuery class
mq = multiQuery()


def app():
    # Streamlit interface code
    st.title("MultiQuery Interface")

    # User input
    user_input = st.text_input("Enter your question:")

    # When the user submits a question
    if st.button("Submit"):
        # Use the multiQuery class to process the question
        response = mq.question_and_answer(user_input)

        # Display the response
        st.write(response)
