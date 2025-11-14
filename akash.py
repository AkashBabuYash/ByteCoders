import streamlit as st
import pyttsx3
import cv2
import numpy as np
import pytesseract
from PyPDF2 import PdfReader
import speech_recognition as sr

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser



google_api_key = "AIzaSyC7-ukc2GbSSvcNER9Z3RamqHuHYBcL-Og"

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=google_api_key
)

prompt = PromptTemplate(
    input_variables=["topic"],
    template="Summarize the following topic into relevant, concise content with 5 to 8 lines:\n\n{topic}"
)

parser = StrOutputParser()
chain = prompt | model | parser



if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

dark_css = """
<style>
body, .stApp {
    background-color: #0e1117 !important;
    color: white !important;
}
textarea, input, .stTextInput>div>div>input {
    background-color: #1c1f26 !important;
    color: white !important;
}
.stButton>button {
    background-color: #3b3f4a !important;
    color: white !important;
    border-radius: 8px;
}
.stSidebar, .css-1d391kg {
    background-color: #0e1117 !important;
}
</style>
"""

light_css = """
<style>
body, .stApp {
    background-color: white !important;
    color: black !important;
}
.stButton>button {
    background-color: #3b3f4a !important;
    color: white !important;
    border-radius: 8px;
}
</style>
"""


if st.session_state.dark_mode:
    st.markdown(dark_css, unsafe_allow_html=True)
else:
    st.markdown(light_css, unsafe_allow_html=True)


mode_label = "🌙 Switch to Light Mode" if st.session_state.dark_mode else "🌞 Switch to Dark Mode"
st.button(mode_label, on_click=toggle_theme)



st.sidebar.title("Choose Mode")

app_mode = st.sidebar.selectbox(
    "Select Option",
    ["Image OCR", "PDF Reader", "Webcam OCR", "Audio to Text", "Input Text"]
)


# ===================== IMAGE OCR ===========================
if app_mode == "Image OCR":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    st.title("📸 Image Text Extractor")
    
    uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        st.image(gray, channels="GRAY", caption="Processed Image")
        text = pytesseract.image_to_string(gray)

        st.subheader("Extracted Text:")
        st.write(text)

        engine = pyttsx3.init()

        if text.strip():
            st.subheader("AI Summary:")
            result = chain.invoke({"topic": text})
            st.write(result)

        if st.button("Get Answer In Audio"):
            engine.say(result)
            engine.runAndWait()

    else:
        st.info("Please upload an image to extract text.")


# ===================== PDF READER ===========================
elif app_mode == "PDF Reader":
    st.title("📚 Multi-PDF Reader")
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        all_text = ""

        for uploaded_file in uploaded_files:
            reader = PdfReader(uploaded_file)
            text = ""

            for page in reader.pages:
                text += page.extract_text() or ""
            
            st.subheader(f"Text from: {uploaded_file.name}")
            st.write(text)
            all_text += text + "\n\n"

        engine = pyttsx3.init()

        if all_text.strip():
            st.subheader("AI Summary:")
            result = chain.invoke({"topic": all_text})
            st.write(result)

        if st.button("Get Answer In Audio"):
            engine.say(result)
            engine.runAndWait()

    else:
        st.info("Upload one or more PDF files to start reading.")


# ===================== WEBCAM OCR ===========================
elif app_mode == "Webcam OCR":
    st.title("🎥 Live Webcam OCR")
    video = cv2.VideoCapture(0)
    frame_window = st.image([])
    capture_button = st.button("Capture Photo")
    captured_frame = None

    while True:
        ret, frame = video.read()
        if not ret:
            st.error("Unable to access the webcam.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.equalizeHist(gray)
        frame_window.image(enhanced, channels="GRAY")

        if capture_button:
            captured_frame = enhanced.copy()
            st.image(captured_frame, caption="Captured Image", channels="GRAY")
            break

    video.release()

    if captured_frame is not None:
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        text = pytesseract.image_to_string(captured_frame)

        st.subheader("Extracted Text:")
        st.write(text)

        engine = pyttsx3.init()

        if text.strip():
            st.subheader("AI Summary:")
            result = chain.invoke({"topic": text})
            st.write(result)

        if st.button("Get Answer In Audio"):
            engine.say(result)
            engine.runAndWait()

    else:
        st.warning("No image captured yet.")


# ===================== AUDIO TO TEXT ===========================
elif app_mode == "Audio to Text":
    st.title("🎤 Audio to Text")
    st.info("Click the button below to start recording.")

    if st.button("Start Recording"):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            st.write("Listening...")
            audio_data = recognizer.listen(source, phrase_time_limit=10)
            st.write("Processing audio...")

            try:
                text = recognizer.recognize_google(audio_data)
                st.success("Transcription Successful:")
                st.write(text)

                engine = pyttsx3.init()

                if text.strip():
                    st.subheader("AI Summary:")
                    result = chain.invoke({"topic": text})
                    st.write(result)

                if st.button("Get Answer In Audio"):
                    engine.say(result)
                    engine.runAndWait()

            except sr.UnknownValueError:
                st.error("Could not understand the audio.")
            except sr.RequestError:
                st.error("Could not connect to Google Speech Recognition service.")


# ===================== TEXT INPUT MODE ===========================
elif app_mode == "Input Text":
    st.title("✍ Text Summarizer")
    text = st.text_area("Enter your text here...")

    engine = pyttsx3.init()

    if text.strip():
        st.subheader("AI Summary:")
        result = chain.invoke({"topic": text})
        st.write(result)

        if st.button("Get Answer In Audio"):
            engine.say(result)
            engine.runAndWait()


# ===================== GENERATE Q/A ===========================
if st.button("Generate Question with Answer"):
    prompt1 = PromptTemplate(
        input_variables=["topic"],
        template="Generate questions and answers from this content:\n\n{topic}"
    )

    chain1 = prompt1 | model | parser
    result1 = chain1.invoke({"topic": text})
    st.write(result1)
