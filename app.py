import streamlit as st
from services.gemini_service import GeminiService
import datetime

gemini = GeminiService()

# 1. Page Configuration
st.set_page_config(
    page_title="DeskPet AI - Terminal 01", 
    page_icon="✈️", 
    layout="wide"
)

# 2. Injecting Custom Retro CSS
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# 3. Initialize Session State for Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "DeskPet AI", "time": "20:44:15", "text": "Hello! 👋 How can I assist you with your journey today?", "class": "ai-msg"}
    ]

# 4. Sidebar Layout
with st.sidebar:
    st.markdown("### ✈️ FLIGHT CONTROLS")
    st.info("Retro Airport Terminal CSS Engine Active.")
    if st.button("Reset Terminal Log"):
        st.session_state.chat_history = [
            {"role": "DeskPet AI", "time": datetime.datetime.now().strftime("%H:%M:%S"), "text": "System cleared. Standing by for commands.", "class": "ai-msg"}
        ]
        st.rerun()

# Titles
st.markdown("<h1 style='text-align: center; color: #00FF66; font-size: 2.5rem;'>✈️ AIRPORT CHATBOX</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>ON THE GO</p>", unsafe_allow_html=True)

# Main Terminal Render
st.markdown('<div class="terminal-frame">', unsafe_allow_html=True)

current_time = datetime.datetime.now().strftime("%H:%M:%S")
st.markdown(f"""
    <div class="terminal-header">
        <div><strong>✈️ DESKPET AI</strong> | TERMINAL 01 | GATE A1</div>
        <div>LOCAL TIME: <span style="color: #FFD700;">{current_time}</span></div>
        <div>STATUS: <span class="status-on-time">ON TIME</span></div>
    </div>
""", unsafe_allow_html=True)

# Loop through and render all messages in history
for msg in st.session_state.chat_history:
    st.markdown(f"""
        <div class="chat-box {msg['class']}">
            <div class="msg-header">
                <span>👤 {msg['role']}</span>
                <span>{msg['time']}</span>
            </div>
            <div>{msg['text']}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 5. Handling User Input & Bot Responses Interactively
def handle_submit():
    user_text = st.session_state.user_message
    if user_text.strip():
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Append User Message
        st.session_state.chat_history.append({
            "role": "You",
            "time": timestamp,
            "text": user_text,
            "class": "user-msg"
        })

        response = gemini.ask(user_text)
        
        # A simple simulated AI response (Replace this with actual LLM code later!)
        ai_timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history.append({
            "role": "DeskPet AI",
            "time": ai_timestamp,
            "text": response,
            "class": "ai-msg"
        })
        
        # Clear the text input box
        st.session_state.user_message = ""

# Layout for the chat input form at the bottom
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        st.text_input(
            "Message Console", 
            placeholder="> Type your message and press Enter...", 
            label_visibility="collapsed",
            key="user_message"
        )
    with col2:
        st.form_submit_button("SEND ✈️", on_click=handle_submit)

# Footer
st.markdown("<hr style='border-color: #2d313f;'><p style='text-align: center; color: #555;'> Have a nice flight! ✈️ </p>", unsafe_allow_html=True)