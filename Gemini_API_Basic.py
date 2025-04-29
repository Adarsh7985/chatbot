import streamlit as st
import google.generativeai as genai

# ✅ Use your actual API key directly here (not recommended for production)
GOOGLE_API_KEY = "AIzaSyBbGUg8UialMhswKKBn9ChB0mQKhVP3mmw"

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# ✅ Use a model that is usually available in the free tier
model = genai.GenerativeModel("models/chat-bison-001")

# Start a chat session
chat = model.start_chat(history=[])

# Function to get Gemini response
def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# Streamlit app setup
st.set_page_config(page_title="Q and A Bot")
st.header("Q and A Bot 🤖")

# Session state to hold chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# User input section
user_input = st.text_input("Enter your question:")
submit = st.button("Submit")

if submit and user_input:
    # Store user message
    st.session_state['chat_history'].append(("You", user_input))

    # Get response from Gemini
    response = get_gemini_response(user_input)
    bot_reply = ""
    for chunk in response:
        st.write(chunk.text)  # Streamed reply
        bot_reply += chunk.text

    # Store bot reply
    st.session_state['chat_history'].append(("Bot", bot_reply))

# Display chat history
st.subheader("Chat History")
for role, text in st.session_state['chat_history']:
    st.markdown(f"**{role}:** {text}")
