import streamlit as st
import datetime


def render_header():

    now = datetime.datetime.now().strftime("%H:%M:%S")

    col1, col2, col3 = st.columns([4, 2, 1])

    with col1:
        st.markdown("""
### ✈ DESKPET AI

**Airport Knowledge Assistant**
""")

    with col2:
        st.metric(
            "Local Time",
            now
        )

    with col3:
        st.success("ONLINE")