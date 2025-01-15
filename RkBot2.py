import streamlit as st
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd

# Configure Google Generative AI API
GOOGLE_API_KEY = "AIzaSyDH5hByP9Okxe8IpO7UYHqImsH24MB6f_Y"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize recognizer and text-to-speech engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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
    if tts_engine._inLoop:  
        tts_engine.endLoop()
    tts_engine.say(text)
    tts_engine.runAndWait()

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
    st.write("Click the microphone button to speak.")
    
    if st.button("🎤 Start Talking"):
        listening_placeholder = st.empty()
        recognized_text = recognize_speech_from_microphone(listening_placeholder)
        if recognized_text:
            with st.spinner("Processing..."):
                processed_text = llm(recognized_text)
                st.session_state.chat_history.append(f"Bot: {processed_text}")
            
            st.subheader("Chat History")
            for message in st.session_state.chat_history:
                st.markdown(f"<p style='color: white; background-color: black; padding: 10px; border-radius: 5px;'>{message}</p>", unsafe_allow_html=True)
            speak_text(processed_text)

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