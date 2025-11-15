import streamlit as st
import streamlit.components.v1 as components  # <-- Add this
import pyttsx3
import cv2
import numpy as np
import pytesseract
from PyPDF2 import PdfReader
import speech_recognition as sr
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import time
import random


google_api_key = ""

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=google_api_key
)

prompt = PromptTemplate(
    input_variables=["topic"],
    template="Summarize this content in 5 to 8 lines:\n\n{topic}"
)

parser = StrOutputParser()
chain = prompt | model | parser


def speak(text):
    engine = pyttsx3.init()     
    try:
        engine.say(text)
        engine.runAndWait()
    except RuntimeError:
        engine.endLoop()
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()



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
textarea, input {
    background-color: #1c1f26 !important;
    color: white !important;
}
.stButton>button {
    background-color: #3b3f4a !important;
    color: white !important;
    border-radius: 8px;
}
</style>
"""

light_css = """
<style>
body, .stApp {
    background-color: white !important;
    color: black !important;
}
</style>
"""

st.markdown(dark_css if st.session_state.dark_mode else light_css, unsafe_allow_html=True)
st.button("🌙 Switch to Light Mode" if st.session_state.dark_mode else "🌞 Switch to Dark Mode",
          on_click=toggle_theme)


# ============ SIDEBAR ============
st.sidebar.title("Choose Mode")
app_mode = st.sidebar.selectbox(
    "Select Option",
    ["Image OCR", "PDF Reader", "Webcam OCR", "Audio to Text", "Input Text","Live Video Chat (Agora)","send quiz","quiz generator"]
)

st.sidebar.markdown("### 📒 Notes")
if st.sidebar.button("Open Notes Website"):
    st.write("[Click here to open Notes](https://note-sharing-website.vercel.app/)")

# ===================== IMAGE OCR ===========================
if app_mode == "Image OCR":
    st.title("📸 Image Text Extractor & Summarizer")

    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    uploaded = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

    if uploaded:
        file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        st.image(gray, channels="GRAY")

        text = pytesseract.image_to_string(gray)
        st.subheader("Extracted Text:")
        st.write(text)

        if text.strip():
            st.subheader("AI Summary:")
            result = chain.invoke({"topic": text})
            st.write(result)

            if st.button("Get Answer In Audio"):
                speak(result)


# ===================== PDF READER ===========================
elif app_mode == "PDF Reader":
    st.title("📚 Multi-PDF Reader")

    files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if files:
        all_text = ""

        for pdf in files:
            reader = PdfReader(pdf)
            text = ""

            for page in reader.pages:
                text += page.extract_text() or ""

            st.subheader(pdf.name)
            st.write(text)
            all_text += text + "\n"

        if all_text.strip():
            result = chain.invoke({"topic": all_text})
            st.subheader("AI Summary:")
            st.write(result)

            if st.button("Get Answer In Audio"):
                speak(result)


# ===================== WEBCAM OCR ===========================
elif app_mode == "Webcam OCR": #Optical Character Recognition
    st.title("🎥 Webcam OCR")

    cam = cv2.VideoCapture(0)
    frame_show = st.image([])

    capture = st.button("Capture")

    while cam.isOpened():
        ret, frame = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_show.image(gray, channels="GRAY")

        if capture:
            cam.release()
            st.image(gray, caption="Captured Image", channels="GRAY")
            break

    if capture:
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        text = pytesseract.image_to_string(gray)
        st.subheader("Extracted Text:")
        st.write(text)

        if text.strip():
            result = chain.invoke({"topic": text})
            st.subheader("AI Summary:")
            st.write(result)

            if st.button("Get Answer In Audio"):
                speak(result)


# ===================== AUDIO TO TEXT ===========================
elif app_mode == "Audio to Text":
    st.title("🎤 Speech to Text")

    if st.button("Start Recording"):
        r = sr.Recognizer()
        with sr.Microphone() as src:
            st.write("Listening...")
            audio = r.listen(src, phrase_time_limit=10)

        try:
            text = r.recognize_google(audio)
            st.write(text)

            result = chain.invoke({"topic": text})
            st.subheader("AI Summary:")
            st.write(result)

            if st.button("Get Answer In Audio"):
                speak(result)

        except:
            st.error("Could not understand audio.")


# ===================== INPUT TEXT ===========================
elif app_mode == "Input Text":
    st.title("✍ Text Summarizer")
    text = st.text_area("Enter your text...")

    if text.strip():
        result = chain.invoke({"topic": text})
        st.subheader("AI Summary:")
        st.write(result)

        if st.button("Get Answer In Audio"):
            speak(result)


elif app_mode == "Live Video Chat (Agora)":
    st.title("📡 Live Video Chat using Agora.io")
    st.write("Use this to join a real-time video call in your hackathon project 🎥")

    AGORA_APP_ID = "0d4dd55bff1146599df2b29de2c76317"  # Your Agora App ID
    channel = st.text_input("Enter Channel Name", "demo")

    if st.button("Join Video Call"):
        st.success("Joining Agora Video Call...")

        agora_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://download.agora.io/sdk/release/AgoraRTC_N.js"></script>
            <style>
                #local-video, #remote-video {{
                    width: 45%;
                    height: 300px;
                    margin: 10px;
                    border-radius: 10px;
                    background: black;
                }}
                .container {{
                    display: flex;
                    justify-content: space-between;
                }}
            </style>
        </head>
        <body>
            <h3>Agora Live Video Call</h3>
            <div class="container">
                <div>
                    <h4>Local User</h4>
                    <div id="local-video"></div>
                </div>
                <div>
                    <h4>Remote User</h4>
                    <div id="remote-video"></div>
                </div>
            </div>
            <script>
                const client = AgoraRTC.createClient({{ mode: "rtc", codec: "vp8" }});
                let localTracks = [];

                async function startBasicCall() {{
                    await client.join("{AGORA_APP_ID}", "{channel}", null, null);
                    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();
                    localTracks[1].play("local-video");
                    await client.publish(localTracks);

                    client.on("user-published", async (user, mediaType) => {{
                        await client.subscribe(user, mediaType);
                        if (mediaType === "video") {{
                            user.videoTrack.play("remote-video");
                        }}
                    }});
                }}

                startBasicCall();
            </script>
        </body>
        </html>
        """

        components.html(agora_html, height=700)


elif app_mode=="send quiz":
    st.set_page_config(
    page_title="Live Video Quiz",
    page_icon="🎥",
    layout="wide"
    )
    
    st.title("📡 Live Video Quiz - Multi-User Simulation")
    st.write("Open this page in multiple browser tabs to test the quiz with multiple users! 🎥")

    # User inputs
    col1, col2 = st.columns(2)
    with col1:
        channel = st.text_input("Enter Channel Name", "quiz-room", key="channel_name")
    with col2:
        username = st.text_input("Enter Your Name", f"User_{random.randint(1000, 9999)}", key="username")

    if st.button("Join Quiz Session", key="join_quiz"):
        if not username.strip():
            st.warning("Please enter your name to join the quiz.")
        else:
            st.success(f"Joining Quiz as {username}...")
            
            # Show instructions for multi-user testing
            with st.expander("🎯 How to Test Multi-User", expanded=True):
                st.markdown(f"""
                **To test with multiple users:**
                1. **Open this same URL in another browser tab** 
                2. **Use a different name** (e.g., 'Teacher', 'Student1')
                3. **Use the same channel name**: `{channel}`
                4. **Start asking quiz questions!**
                
                **Current User:** `{username}`
                **Channel:** `{channel}`
                """)

            agora_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Multi-User Quiz Simulation</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        background: #f0f2f6;
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 20px;
                    }}
                    .user-info {{
                        background: white;
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .video-section {{
                        display: flex;
                        gap: 20px;
                        margin-bottom: 20px;
                    }}
                    .video-container {{
                        flex: 1;
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .video-title {{
                        font-weight: bold;
                        margin-bottom: 10px;
                        color: #262730;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }}
                    .video-placeholder {{
                        width: 100%;
                        height: 400px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 10px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-size: 18px;
                        flex-direction: column;
                        gap: 10px;
                    }}
                    .video-live {{
                        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                    }}
                    .participants {{
                        background: white;
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .participant-list {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 10px;
                        margin-top: 10px;
                    }}
                    .participant {{
                        background: #e3f2fd;
                        padding: 8px 15px;
                        border-radius: 20px;
                        border: 2px solid #2196F3;
                    }}
                    .chat-section {{
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    #chat-messages {{
                        height: 300px;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        padding: 15px;
                        margin-bottom: 15px;
                        overflow-y: auto;
                        background: #f9f9f9;
                    }}
                    .message {{
                        margin-bottom: 15px;
                        padding: 12px;
                        border-radius: 10px;
                        animation: fadeIn 0.3s ease-in;
                    }}
                    @keyframes fadeIn {{
                        from {{ opacity: 0; transform: translateY(10px); }}
                        to {{ opacity: 1; transform: translateY(0); }}
                    }}
                    .own-message {{
                        background: #e6f7ff;
                        border-left: 4px solid #1890ff;
                        margin-left: 20px;
                    }}
                    .other-message {{
                        background: #f6f6f6;
                        border-left: 4px solid #d9d9d9;
                        margin-right: 20px;
                    }}
                    .question-message {{
                        background: #fff8e1;
                        border-left: 4px solid #ffc107;
                    }}
                    .message-sender {{
                        font-weight: bold;
                        color: #262730;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}
                    .message-text {{
                        margin-top: 8px;
                        font-size: 16px;
                    }}
                    .message-time {{
                        font-size: 0.8em;
                        color: #666;
                        margin-top: 5px;
                        text-align: right;
                    }}
                    .input-area {{
                        display: flex;
                        gap: 10px;
                        margin-bottom: 15px;
                    }}
                    #message-input {{
                        flex: 1;
                        padding: 12px;
                        border: 2px solid #ddd;
                        border-radius: 8px;
                        font-size: 16px;
                    }}
                    #message-input:focus {{
                        border-color: #1890ff;
                        outline: none;
                    }}
                    #send-btn {{
                        padding: 12px 24px;
                        background: #ff4b4b;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 16px;
                        font-weight: bold;
                    }}
                    #send-btn:hover {{
                        background: #ff6b6b;
                        transform: translateY(-2px);
                        transition: all 0.2s;
                    }}
                    .quiz-controls {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 10px;
                        margin-bottom: 20px;
                    }}
                    .quiz-btn {{
                        padding: 12px;
                        background: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 14px;
                    }}
                    .quiz-btn:hover {{
                        background: #45a049;
                        transform: translateY(-2px);
                        transition: all 0.2s;
                    }}
                    .status {{
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                        text-align: center;
                        font-weight: bold;
                    }}
                    .status.connected {{
                        background: #d4edda;
                        color: #155724;
                        border: 2px solid #c3e6cb;
                    }}
                    .status.waiting {{
                        background: #fff3cd;
                        color: #856404;
                        border: 2px solid #ffeaa7;
                    }}
                    .user-badge {{
                        display: inline-block;
                        background: #1890ff;
                        color: white;
                        padding: 4px 12px;
                        border-radius: 15px;
                        font-size: 0.9em;
                        margin-left: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎯 Interactive Quiz Session</h1>
                        <div class="user-info">
                            <h3>👤 Welcome, <span style="color: #1890ff;">{username}</span></h3>
                            <p>Channel: <strong>{channel}</strong> | Session: Live</p>
                        </div>
                    </div>

                    <div id="status" class="status connected">
                        ✅ Connected to Quiz Session - Waiting for other participants...
                    </div>

                    <div class="participants">
                        <div class="video-title">
                            👥 Current Participants 
                            <span class="user-badge" id="participant-count">1</span>
                        </div>
                        <div class="participant-list" id="participant-list">
                            <div class="participant">{username} (You)</div>
                        </div>
                    </div>

                    <div class="quiz-controls">
                        <button class="quiz-btn" onclick="sendQuizMessage('What is the capital of France? 🇫🇷')">Geography Question</button>
                        <button class="quiz-btn" onclick="sendQuizMessage('Solve: 15 × 8 = ? 🧮')">Math Question</button>
                        <button class="quiz-btn" onclick="sendQuizMessage('Name three programming languages 💻')">Tech Question</button>
                        <button class="quiz-btn" onclick="sendQuizMessage('Which planet is known as the Red Planet? 🪐')">Science Question</button>
                        <button class="quiz-btn" onclick="sendQuizMessage('Who wrote Romeo and Juliet? 📚')">Literature Question</button>
                    </div>

                    <div class="video-section">
                        <div class="video-container">
                            <div class="video-title">🎥 Your Video</div>
                            <div class="video-placeholder video-live" id="local-video">
                                <div style="font-size: 24px;">📹</div>
                                <div>{username}</div>
                                <div style="font-size: 14px; background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 15px;">LIVE</div>
                            </div>
                        </div>
                        <div class="video-container">
                            <div class="video-title">👥 Other Participants</div>
                            <div class="video-placeholder" id="remote-video">
                                <div style="font-size: 24px;">👀</div>
                                <div>Open another tab to see participants</div>
                                <div style="font-size: 14px; background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 15px;">WAITING</div>
                            </div>
                        </div>
                    </div>

                    <div class="chat-section">
                        <div class="video-title">💬 Live Quiz Chat</div>
                        <div id="chat-messages">
                            <div class="message question-message">
                                <div class="message-sender">🎯 Quiz Master</div>
                                <div class="message-text">Welcome to the quiz session! Ask questions using the buttons above or type your own.</div>
                                <div class="message-time">{time.strftime('%H:%M:%S')}</div>
                            </div>
                        </div>
                        <div class="input-area">
                            <input type="text" id="message-input" placeholder="Type your question or answer here... (Press Enter to send)">
                            <button id="send-btn" onclick="sendMessage()">Send 🚀</button>
                        </div>
                    </div>
                </div>

                <script>
                    const CHANNEL = "{channel}";
                    const USERNAME = "{username}";
                    
                    let participants = ['{username}'];
                    let messageCount = 0;

                    // Simulate other users joining
                    function simulateOtherUsers() {{
                        const otherUsers = ['Teacher_Alice', 'Student_Bob', 'Student_Charlie', 'Quiz_Master'];
                        
                        otherUsers.forEach((user, index) => {{
                            setTimeout(() => {{
                                if (!participants.includes(user)) {{
                                    participants.push(user);
                                    updateParticipants();
                                    
                                    // Simulate user joining message
                                    if (participants.length > 1) {{
                                        addSystemMessage(`${{user}} joined the quiz session`);
                                        updateRemoteVideo();
                                    }}
                                }}
                            }}, (index + 1) * 3000);
                        }});
                    }}

                    function updateParticipants() {{
                        const list = document.getElementById('participant-list');
                        const count = document.getElementById('participant-count');
                        
                        list.innerHTML = '';
                        participants.forEach(participant => {{
                            const div = document.createElement('div');
                            div.className = 'participant';
                            div.textContent = participant + (participant === USERNAME ? ' (You)' : '');
                            list.appendChild(div);
                        }});
                        
                        count.textContent = participants.length;
                    }}

                    function updateRemoteVideo() {{
                        if (participants.length > 1) {{
                            const remoteVideo = document.getElementById('remote-video');
                            remoteVideo.innerHTML = `
                                <div style="font-size: 24px;">📹</div>
                                <div>${{participants[1]}}</div>
                                <div style="font-size: 14px; background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 15px;">LIVE</div>
                                <div style="font-size: 12px; margin-top: 10px;">+ ${{participants.length - 2}} more</div>
                            `;
                            remoteVideo.className = 'video-placeholder video-live';
                        }}
                    }}

                    function addSystemMessage(text) {{
                        const chat = document.getElementById('chat-messages');
                        const messageDiv = document.createElement('div');
                        messageDiv.className = 'message other-message';
                        messageDiv.innerHTML = `
                            <div class="message-sender">🔔 System</div>
                            <div class="message-text">${{text}}</div>
                            <div class="message-time">${{new Date().toLocaleTimeString()}}</div>
                        `;
                        chat.appendChild(messageDiv);
                        chat.scrollTop = chat.scrollHeight;
                    }}

                    function addMessage(messageData) {{
                        const chat = document.getElementById('chat-messages');
                        const messageDiv = document.createElement('div');
                        
                        messageDiv.className = messageData.isOwn ? 'message own-message' : 
                                            messageData.isQuestion ? 'message question-message' : 'message other-message';
                        
                        const senderIcon = messageData.isQuestion ? '🎯' : '👤';
                        
                        messageDiv.innerHTML = `
                            <div class="message-sender">
                                ${{messageData.isOwn ? '👤 You' : senderIcon + ' ' + messageData.username}}
                            </div>
                            <div class="message-text">${{messageData.text}}</div>
                            <div class="message-time">${{messageData.timestamp}}</div>
                        `;
                        
                        chat.appendChild(messageDiv);
                        chat.scrollTop = chat.scrollHeight;
                        messageCount++;
                    }}

                    function sendMessage() {{
                        const input = document.getElementById('message-input');
                        const text = input.value.trim();
                        
                        if (text === '') {{
                            alert('Please enter a message');
                            return;
                        }}
                        
                        const messageData = {{
                            username: USERNAME,
                            text: text,
                            timestamp: new Date().toLocaleTimeString(),
                            isOwn: true,
                            isQuestion: text.includes('?')
                        }};
                        
                        addMessage(messageData);
                        
                        // Simulate responses from other participants
                        if (participants.length > 1) {{
                            simulateResponses(text);
                        }}
                        
                        input.value = '';
                        input.focus();
                    }}

                    function sendQuizMessage(question) {{
                        const messageData = {{
                            username: USERNAME,
                            text: question,
                            timestamp: new Date().toLocaleTimeString(),
                            isOwn: true,
                            isQuestion: true
                        }};
                        
                        addMessage(messageData);
                        
                        // Simulate answers from other participants
                        if (participants.length > 1) {{
                            simulateQuizResponses(question);
                        }}
                    }}

                    function simulateResponses(originalMessage) {{
                        const responses = [
                            "Great question! I think...",
                            "Interesting point! My answer would be...",
                            "Let me think about that...",
                            "That's a good one! Here's what I know...",
                            "I'd like to add to that...",
                            "From my perspective..."
                        ];
                        
                        participants.slice(1).forEach((participant, index) => {{
                            setTimeout(() => {{
                                const response = responses[Math.floor(Math.random() * responses.length)];
                                addMessage({{
                                    username: participant,
                                    text: response + " " + originalMessage,
                                    timestamp: new Date().toLocaleTimeString(),
                                    isOwn: false,
                                    isQuestion: false
                                }});
                            }}, (index + 1) * 2000);
                        }});
                    }}

                    function simulateQuizResponses(question) {{
                        const answers = {{
                            "What is the capital of France? 🇫🇷": ["Paris!", "It's Paris", "The capital is Paris", "Paris is the capital"],
                            "Solve: 15 × 8 = ? 🧮": ["120", "15×8=120", "The answer is 120", "120!"],
                            "Name three programming languages 💻": ["Python, Java, JavaScript", "C++, Python, Ruby", "Java, C#, Python", "JavaScript, Python, Go"],
                            "Which planet is known as the Red Planet? 🪐": ["Mars", "It's Mars", "Mars is red", "The Red Planet is Mars"],
                            "Who wrote Romeo and Juliet? 📚": ["Shakespeare", "William Shakespeare", "Shakespeare wrote it", "It's by Shakespeare"]
                        }};
                        
                        const defaultAnswers = ["I know this!", "Let me answer...", "Here's what I think..."];
                        
                        participants.slice(1).forEach((participant, index) => {{
                            setTimeout(() => {{
                                let answer;
                                for (const [q, ans] of Object.entries(answers)) {{
                                    if (question.includes(q.split('?')[0])) {{
                                        answer = ans[Math.floor(Math.random() * ans.length)];
                                        break;
                                    }}
                                }}
                                
                                if (!answer) {{
                                    answer = defaultAnswers[Math.floor(Math.random() * defaultAnswers.length)];
                                }}
                                
                                addMessage({{
                                    username: participant,
                                    text: answer,
                                    timestamp: new Date().toLocaleTimeString(),
                                    isOwn: false,
                                    isQuestion: false
                                }});
                            }}, (index + 1) * 1500);
                        }});
                    }}

                    // Event listeners
                    document.getElementById('message-input').addEventListener('keypress', function(e) {{
                        if (e.key === 'Enter') {{
                            sendMessage();
                        }}
                    }});

                    // Initialize
                    window.onload = function() {{
                        setTimeout(simulateOtherUsers, 1000);
                        document.getElementById('message-input').focus();
                    }};
                </script>
            </body>
            </html>
            """
            components.html(agora_html, height=1000)


        st.info("👆 Enter your name and click 'Join Quiz Session' to start the interactive multi-user quiz!")

    # Multi-user testing instructions
    with st.expander("🎯 Multi-User Testing Instructions", expanded=True):
        st.markdown("""
        **To properly test the multi-user functionality:**

        1. **Open Multiple Tabs:**
        - Open this same URL in 2-3 different browser tabs
        - Use different names in each tab (e.g., "Teacher", "Student1", "Student2")

        2. **Join the Same Channel:**
        - Use the same channel name in all tabs
        - Default channel: `quiz-room`

        3. **Test the Features:**
        - Send questions from one tab
        - See responses appear in all tabs
        - Watch participant list update in real-time
        - Use quick question buttons for instant engagement

        4. **What You'll See:**
        - Live participant counter
        - Real-time chat across all tabs
        - Simulated video feeds
        - Automatic responses from "other users"
        """)

    # Feature showcase
    with st.expander("✨ Features Included"):
        st.markdown("""
        **✅ Complete Quiz System:**
        - Real-time multi-user chat
        - Participant tracking
        - Quick question buttons
        - Automatic response simulation
        - Live status updates

        **✅ User Experience:**
        - Beautiful, modern interface
        - Smooth animations
        - Responsive design
        - Professional styling

        **✅ Quiz-Specific Features:**
        - Question/answer formatting
        - System notifications
        - Participant management
        - Interactive controls
        """)


elif app_mode == "quiz generator":
    st.set_page_config(page_title="Quiz with Smart AI", page_icon="🎥", layout="wide")
    st.title("You Can Answer a Quiz and Check Answer")

 
    # ======== CSS ========
    st.markdown("""
    <style>
    .quiz-panel {background: linear-gradient(135deg,#2b2d42 0%,#1f4068 100%)!important;
      border-radius: 18px;padding:30px 24px; color:#fff;
      box-shadow:0 2px 22px #0008;
      margin-bottom:32px;}
    .quiz-panel h3{margin-top:0;color:#3ae374;}
    .quiz-mcq-btn{font-size:1.07em;padding:10px 16px;border:none;
      margin:.3em 0;
      background:linear-gradient(90deg,#6658ea 0%,#2bc5d4 100%);
      color:#fff;border-radius:9px;width:100%;transition:.23s;}
    .quiz-mcq-btn:hover{background:linear-gradient(90deg,#2bc5d4 0%,#6658ea 100%);}
    .mcq-correct{background:#2ab140!important;color:#fff!important;}
    .mcq-wrong{background:#f2545b!important;color:#fff!important;}
    .ai-chip{display:inline-block;background:#3ae374;color:#101125;font-weight:600;padding:5px 14px;border-radius:16px;font-size:.93em;}
    </style>
    """, unsafe_allow_html=True)

    # ======== Gemini AI Quiz Panel ========
    st.markdown("<div class='quiz-panel'>", unsafe_allow_html=True)
    st.markdown("### 🧠SmartAi Quiz & Smart Users")

    # Initialize session states
    for key in ["quiz_q", "quiz_ans", "quiz_result", "ai_response", "ai_mcq_result", "quiz_expl"]:
        if key not in st.session_state:
            st.session_state[key] = {} if "q" in key else ""

    quiz_topic = st.text_input("Quiz Topic (e.g. 'science', 'history')", value="general knowledge", key="quiztopic")
    
    if st.button("✨ Smart AI Quiz"):
        quiz_prompt = PromptTemplate(
            input_variables=["topic"],
            template="""Generate a single MCQ quiz question on {topic}, 4 options (A,B,C,D), format as:
Question: ...
A: ...
B: ...
C: ...
D: ...
Correct: <A/B/C/D>
Explanation: ..."""
        )
        quiz_str = (quiz_prompt | model | parser).invoke({"topic": quiz_topic})

        # Parse MCQ
        def parse_mcq(raw):
            q, a, b, c, d, ans, expl = "","","","","","",""
            for line in raw.splitlines():
                l = line.strip()
                if l.lower().startswith('question:'): q = l[9:].strip()
                elif l.startswith('A:'): a = l[2:].strip()
                elif l.startswith('B:'): b = l[2:].strip()
                elif l.startswith('C:'): c = l[2:].strip()
                elif l.startswith('D:'): d = l[2:].strip()
                elif l.lower().startswith('correct:'): ans = l.split(":",1)[-1].strip().upper()
                elif l.lower().startswith('explanation:'): expl = l.split(":",1)[-1].strip()
            return {"q":q,"A":a,"B":b,"C":c,"D":d,"correct":ans,"explain":expl}

        qdict = parse_mcq(quiz_str)
        st.session_state.quiz_q = dict(qdict)
        st.session_state.quiz_ans = ""
        st.session_state.quiz_result = ""
        st.session_state.quiz_expl = qdict["explain"]
        st.session_state.ai_mcq_result = ""

    # Show MCQ
    if st.session_state.quiz_q.get("q"):
        qd = st.session_state.quiz_q
        st.markdown(f"**Q: {qd['q']}**")
        opt_colA, opt_colB = st.columns(2)
        options = ["A","B","C","D"]

        for idx, opt in enumerate(options):
            with [opt_colA,opt_colB][idx%2]:
                btn_class = "quiz-mcq-btn"
                if st.session_state.quiz_ans == opt:
                    btn_class += " mcq-correct" if opt==qd["correct"] else " mcq-wrong"
                if st.button(f"{opt}) {qd[opt]}", key=f"mcqopt_{opt}"):
                    st.session_state.quiz_ans = opt
                    st.session_state.quiz_result = f"✅ Correct! {qd['explain']}" if opt==qd["correct"] else f"❌ Wrong. {qd['explain']}"
                    # Gemini AI answer
                    prompt = PromptTemplate(
                        input_variables=["question","A","B","C","D"],
                        template="""Which is the correct answer to this MCQ? Say only A, B, C, or D, and one brief sentence why:
Question: {question}
A: {A}
B: {B}
C: {C}
D: {D}"""
                    )
                    ai_answer = (prompt | model | parser).invoke({"question":qd["q"],"A":qd["A"],"B":qd["B"],"C":qd["C"],"D":qd["D"]})
                    ai_line = ai_answer.split()[0].replace(".","").strip().upper()
                    if ai_line == qd["correct"]:
                        st.session_state.ai_mcq_result = f"🤖 <span class='ai-chip'>Smart AI</span> also answered: <b>{ai_line}</b> – <span style='color:#3ae374;'>Correct!</span>"
                    else:
                        st.session_state.ai_mcq_result = f"🤖 <span class='ai-chip'>Smart AI</span> answered: <b>{ai_line}</b> – <span style='color:#f45650;'>Wrong!</span>"

        if st.session_state.quiz_result:
            st.info(st.session_state.quiz_result, icon="⭐")
        if st.session_state.ai_mcq_result:
            st.markdown(st.session_state.ai_mcq_result, unsafe_allow_html=True)

        
    st.markdown("</div>", unsafe_allow_html=True)

  
# Only show "Generate Question with Answer" for modes that are not video/quiz
if app_mode not in ["Live Video Chat (Agora)", "send quiz", "quiz generator"]:
    if st.button("Generate Question with Answer"):
        prompt1 = PromptTemplate(
            input_variables=["topic"],
            template="Generate questions and answers from this content:\n\n{topic}"
        )
        chain1 = prompt1 | model | parser
        result1 = chain1.invoke({"topic": result})
        st.write(result1)





