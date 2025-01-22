# Streamlit Title Section
import streamlit as st

st.markdown(
    """
    <style>
    .main-heading {
        font-size: 50px;
        font-weight: bold;
        color: #4CAF50; /* Change color as needed */
        text-align: center;
        margin-top: 20px;
    }
    .side-heading {
        font-size: 24px;
        font-weight: normal;
        color: #555; /* Change color as needed */
        text-align: center;
        margin-top: -10px;
    }
    </style>
    <div>
        <h1 class="main-heading">VocaSynth</h1>
        <h2 class="side-heading">A Universal Voice Companion</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Import Libraries
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import base64

# Configure Google Generative AI API
GOOGLE_API_KEY = "YOUR_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize recognizer and text-to-speech engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_speaking" not in st.session_state:
    st.session_state.is_speaking = False

# LLM function
def llm(text): 
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(text)
    return response.text.capitalize()

# Speech recognition function
def recognize_speech_from_microphone(listening_placeholder):
    with sr.Microphone() as source:
        listening_placeholder.info("Listening...")
        try:
            audio = recognizer.record(source, duration=3)
            text = recognizer.recognize_google(audio)
            st.session_state.chat_history.append(f"You: {text.capitalize()}")
            listening_placeholder.empty()
            return text
        except sr.UnknownValueError:
            listening_placeholder.error("Could not understand the audio")
        except sr.RequestError:
            listening_placeholder.error("Could not request results from the service")
        return None

# Text-to-speech function
def speak_text(text):
    st.session_state.is_speaking = True
    if tts_engine._inLoop:  
        tts_engine.endLoop()
    tts_engine.say(text)
    tts_engine.runAndWait()
    st.session_state.is_speaking = False

# Function to stop text-to-speech
def stop_speech():
    if tts_engine._inLoop:
        tts_engine.stop()
    st.session_state.is_speaking = False

# Function to read file content
def read_file_content(uploaded_file):
    file_type = uploaded_file.type
    if "pdf" in file_type:
        reader = PdfReader(uploaded_file)
        content = "\n".join(page.extract_text() for page in reader.pages)
    elif "word" in file_type or "msword" in file_type or "officedocument" in file_type:
        doc = Document(uploaded_file)
        content = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    elif "excel" in file_type or "spreadsheetml" in file_type:
        df = pd.read_excel(uploaded_file)
        content = df.to_string(index=False)
    elif "text" in file_type or "plain" in file_type:
        content = uploaded_file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file type")
    return content

# Summarization function
def summarize_document(content):
    prompt = f"Summarize the following document:\n{content}"
    return llm(prompt)

# Streamlit Tabs
tab1, tab2 = st.tabs(["🤖 Speaking Bot", "📄 Document Summarization"])

# Tab 1: Speaking Bot
with tab1:
    st.subheader("Speaking Bot")
    st.write("Click the microphone button to speak or stop the response.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎤 Start Talking"):
            listening_placeholder = st.empty()
            recognized_text = recognize_speech_from_microphone(listening_placeholder)
            if recognized_text:
                with st.spinner("Processing..."):
                    processed_text = llm(recognized_text)
                    st.session_state.chat_history.append(f"Bot: {processed_text}")
                
                st.subheader("Chat History")
                for message in st.session_state.chat_history:
                    # Escape special characters
                    safe_message = message.replace("*", "\\*")
                    st.markdown(
                        f"<p style='color: white; background-color: black; padding: 10px; border-radius: 5px;'>{safe_message}</p>",
                        unsafe_allow_html=True,
                    )
                
                # Set speaking state and start speech
                st.session_state.is_speaking = True
                speak_text(processed_text)

    with col2:
        if st.button("🛑 Stop"):
            stop_speech()
            st.info("Speech stopped.")

# Tab 2: Document Summarization
with tab2:
    st.subheader("Document Summarization")
    uploaded_file = st.file_uploader("Upload a document (PDF, Word, Excel, or TXT)", type=["pdf", "docx", "xlsx", "txt"])

    if uploaded_file:
        try:
            with st.spinner("Reading file content..."):
                document_content = read_file_content(uploaded_file)
            st.text_area("Uploaded Document", document_content, height=200)

            if st.button("Summarize Document"):
                with st.spinner("Summarizing document..."):
                    summary = summarize_document(document_content)
                st.subheader("Document Summary")
                st.write(summary)
        except Exception as e:
            st.error(f"Error processing the file: {e}")

# Function to set background image
def add_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

add_background("E:/Project/BG/2.png")
