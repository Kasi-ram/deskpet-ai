import streamlit as st

st.set_page_config(
    page_title="DeskPet AI",
    page_icon="🤖"
)

st.title("DeskPet AI")

st.write("Hello Kasi!")

question = st.text_input("Ask me anything")

if question:
    st.write("You asked:")
    st.write(question)