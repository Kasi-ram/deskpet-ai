import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.header("Knowledge Base")

        st.success("BritishAirways.pdf")

        st.success("DGCA.pdf")

        st.success("RefundPolicy.pdf")

        st.divider()

        st.header("System")

        st.write("LLM : Gemini Flash")

        st.write("Vector DB : ChromaDB")

        st.write("Documents : 3")

        st.write("Chunks : 503")

        st.divider()

        st.file_uploader(
            "Upload PDF",
            type="pdf"
        )