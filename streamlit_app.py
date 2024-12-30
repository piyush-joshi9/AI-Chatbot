import streamlit as st
import os
import requests
import json
import speech_recognition as sr
import base64
import time
from requests.exceptions import ConnectionError
from gtts import gTTS
import tempfile
from chatbot import Chatbot  # Import the Chatbot class

# Page config
st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="wide")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True  # Set to True to bypass login

# Initialize the Chatbot instance
weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY", "529d501feabd8b5206c45478a453b991")
google_api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyBjCBFX0T0KbXo4h_LNu1sDhmwre1hpCow")
cse_id = os.getenv("GOOGLE_CSE_ID", "a1c48fad8fa4c4f0e")
chatbot = Chatbot(weather_api_key, google_api_key, cse_id)

# Function to get voice input from the user
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.write(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            st.error("Could not request results from Google Speech Recognition service.")
            return None

# Function to show typing indicator
def show_typing_indicator():
    with st.spinner("Typing..."):
        time.sleep(1)  # Simulate typing delay

# Function to convert text to speech
def speak_text(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(f"{fp.name}.mp3")
        os.system(f"start {fp.name}.mp3")  # This will play the audio file

# Function to display the chatbot interface
def display_chatbot():
    st.title("Welcome to the Chatbot")
    st.markdown(
        """
        <div class="typewriter">
            <h1>What can I help you with?</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history with unique keys and bubble effect
    with chat_container:
        for idx, message in enumerate(st.session_state.messages):
            # Define avatar paths using relative paths
            if message["role"] == "assistant":
                avatar_path = "125886727_Cartoon Style Robot.jpg"  # Assistant avatar path
            else:
                avatar_path = "125887131_Chatbot Message Bubble.jpg"  # User avatar path

            with st.chat_message(message["role"]):
               col1, col2 = st.columns([0.1, 0.9])  # Create two columns for avatar and message
            with col1:
                st.image(avatar_path, width=40, caption="", use_container_width=True)  # Display avatar
            with col2:
                st.markdown(
                    f"""
                    <div class="chat-bubble {message['role']}">
                        <p>{message['content']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            if message["role"] == "assistant":
                if st.button("🔊", key=f"speak_{idx}_{message['content'][:10]}"):
                    speak_text(message["content"])
    
    # Input container
    with st.form(key="message_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 0.5, 0.5])
        
        with col1:
            user_input = st.text_input("Type or speak your message...", key="user_input")
        with col2:
            send_button = st.form_submit_button("Send")
        with col3:
            voice_button = st.form_submit_button("🎤")
    
    # Handle voice input
    if voice_button:
        voice_input = get_voice_input()
        if voice_input:
            user_input = voice_input
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            show_typing_indicator()
            bot_response = chatbot.get_response(user_input)
            if bot_response:
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                speak_text(bot_response)
            st.rerun()
    
    # Handle text input
    elif user_input and send_button:
        st.session_state.messages.append({"role": "user", "content": user_input})
        show_typing_indicator()
        bot_response = chatbot.get_response(user_input)
        if bot_response:
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.rerun()

# Main interface
def main():
    # Set background style and animations
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            color: white;
        }

        @keyframes gradient {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }

        .login-container, .signup-container {
            background: rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            animation: fadeIn 0.5s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        input, button {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border: none;
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }

        button {
            background: #4CAF50;
            cursor: pointer;
            transition: background 0.3s ease;
        }

        button:hover {
            background: #45a049;
        }

        .typewriter h1 {
            overflow: hidden;
            border-right: .15em solid orange;
            white-space: nowrap;
            margin: 0 auto;
            letter-spacing: .15em;
            animation: typing 3.5s steps(40, end), blink-caret .75s step-end infinite;
        }

        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }

        @keyframes blink-caret {
            from, to { border-color: transparent }
            50% { border-color: orange; }
        }

        .chat-bubble {
            padding: 10px 15px;
            border-radius: 20px;
            margin: 10px 0;
            max-width: 80%;
            animation: bubbleFloat 0.5s ease-out;
        }

        @keyframes bubbleFloat {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .chat-bubble.user {
            background-color: #4CAF50;
            align-self: flex-end;
        }

        .chat-bubble.assistant {
            background-color: #2196F3;
            align-self: flex-start;
        }

        .stTextInput, .stButton {
            background-color: rgba(255, 255, 255, 0.2) !important;
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
        }

        .stButton:hover {
            background-color: rgba(255, 255, 255, 0.3) !important;
        }
        </style>

        <script>
        function playProcessingSound() {
            var audio = new Audio('path_to_your_sound_file.mp3');
            audio.play();
        }

        document.addEventListener('DOMContentLoaded', (event) => {
            playProcessingSound();
        });
        </script>
        """,
        unsafe_allow_html=True
    )
    
    # Display the chatbot interface directly
    display_chatbot()

if __name__ == "__main__":
    main()

