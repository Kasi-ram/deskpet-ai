import uuid

import streamlit as st

from services.langgraph_agent import LangGraphAgent


st.set_page_config(
    page_title="DeskPet AI",
    page_icon="✈️"
)


@st.cache_resource
def load_agent():
    return LangGraphAgent()


agent = load_agent()


if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(
        uuid.uuid4()
    )


if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("DeskPet AI")

st.caption(
    "Agentic Airline Knowledge Assistant"
)


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )

        if message.get("sources"):

            st.caption("Sources")

            for source in message["sources"]:

                st.caption(
                    f'{source["source"]} '
                    f'- Page {source["page"]}'
                )


question = st.chat_input(
    "Ask about airline policies..."
)


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)


    with st.chat_message("assistant"):

        with st.status(
            "DeskPet is working...",
            expanded=True
        ) as status:

            st.write(
                "Understanding your request..."
            )

            response = {
                "answer": "",
                "sources": []
            }

            node_messages = {
                "planner": "Planning request...",
                "knowledge": "Searching airline knowledge...",
                "calculator": "Running calculator...",
                "general": "Answering general question...",
                "final_answer": "Preparing final answer..."
            }

            for event in agent.stream(
                question,
                thread_id=st.session_state.thread_id
            ):

                if event["type"] == "node":

                    node_name = event["node"]

                    message = node_messages.get(
                        node_name
                    )

                    if message:
                        st.write(message)

                elif event["type"] == "result":

                    response = {
                        "answer": event["answer"],
                        "sources": event["sources"]
                    }

            status.update(
                label="Completed",
                state="complete",
                expanded=False
            )


        st.markdown(
            response["answer"]
        )


        if response["sources"]:

            st.caption("Sources")

            for source in response["sources"]:

                st.caption(
                    f'{source["source"]} '
                    f'- Page {source["page"]}'
                )


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response["answer"],
            "sources": response["sources"]
        }
    )


with st.sidebar:

    st.header("DeskPet AI")

    st.write(
        "LangGraph Agent"
    )

    st.write(
        "Knowledge Tool"
    )

    st.write(
        "Calculator Tool"
    )


    if st.button("New Conversation"):

        st.session_state.messages = []

        st.session_state.thread_id = str(
            uuid.uuid4()
        )

        st.rerun()