import streamlit as st


def render_chat(history):

    for message in history:

        role = (
            "assistant"
            if message["role"] == "DeskPet AI"
            else "user"
        )

        with st.chat_message(role):

            st.markdown(
                message["text"]
            )