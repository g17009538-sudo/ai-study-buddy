import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import datetime
from youtube_transcript_api import YouTubeTranscriptApi

# App UI & Custom Design
st.set_page_config(page_title="AI Study Tutor", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FEF5F0; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 2px solid #F48024; }
    .stButton>button { border-radius: 20px; border: 1px solid #F48024; color: #F48024; }
    .stButton>button:hover { background-color: #F48024; color: white; }
    .study-box { background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #F48024; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception:
    st.error("⚠️ API key is missing in Streamlit Secrets.")
    st.stop()

# Session States for Memory & Gamification
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Main tumhara AI Tutor hoon. Kuch upload karo ya seedha sawaal poocho! 😊"}]
if "score" not in st.session_state:
    st.session_state.score = 0
if "study_plan" not in st.session_state:
    st.session_state.study_plan = None
if "context_text" not in st.session_state:
    st.session_state.context_text = ""
if "img_data" not in st.session_state:
    st.session_state.img_data = None

# Sidebar: Gamification & Settings
with st.sidebar:
    st.metric(label="🔥 Study Streak & Points", value=f"{st.session_state.score} XP")
    st.divider()
    app_mode = st.radio("Mode Select Karo:", ["💬 Chat & Tools", "📅 Exam Prep Wizard"])
    st.divider()
    pref_lang = st.selectbox("Language / Bhasha:", ["English", "Hinglish", "Hindi", "Telugu"])
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = [{"role": "assistant", "content": "Chat cleared!"}]
        st.rerun()

st.title("🎓 Smart AI Study Tutor")

# Mode 1: Exam Prep Wizard (Animated & Boxed)
if app_mode == "📅 Exam Prep Wizard":
    st.subheader("Interactive Exam Planner")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        exam_subject = st.text_input("Subject", placeholder="e.g., JEE Main Physics")
    with col2:
        exam_date = st.date_input("Exam Date", min_value=datetime.date.today())
    with col3:
        target_score = st.text_input("Target Score", placeholder="e.g., 250+ or 95%")
        
    if st.button("🚀 Create Path"):
        if not st.session_state.context_text:
            st.warning("Pehle Chat mode mein jaakar '+' icon se notes ya video upload karo!")
        elif exam_subject:
            days_left = (exam_date - datetime.date.today()).days
            with st.spinner("Analyzing syllabus... Creating your personalized path..."):
                prompt = f"Create a day-by-day study plan for {exam_subject} exam in {days_left} days. Target: {target_score}. Use this context: {st.session_state.context_text[:3000]}. Format EXACTLY like this: 'DAY 1: Topic Name - Details|DAY 2: Topic Name - Details'."
                response = model.generate_content(prompt)
                st.session_state.study_plan = response.text.split('|')
                st.rerun()

    # Show Day-by-Day Boxes with Checkboxes
    if st.session_state.study_plan:
        st.markdown("### 🗓️ Your Custom Study Plan")
        for i, day_task in enumerate(st.session_state.study_plan):
            if day_task.strip():
                st.markdown(f'<div class="study-box">{day_task}</div>', unsafe_allow_html=True)
                if st.checkbox(f"✅ Mark Day {i+1} as Done", key=f"day_{i}"):
                    st.session_state.score += 10

# Mode 2: Chat & Tools (With "+" Icon and Voice)
elif app_mode == "💬 Chat & Tools":
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Layout for Chat Input and + Icon
    chat_col, plus_col = st.columns([8, 1])
    
    with plus_col:
        with st.popover("➕ Add"):
            st.write("Upload Material")
            up_pdf = st.file_uploader("📝 PDF Notes", type="pdf")
            if up_pdf:
                st.session_state.context_text = "".join(page.extract_text() for page in PyPDF2.PdfReader(up_pdf).pages if page.extract_text())
                st.success("PDF Saved!")
                
            up_img = st.file_uploader("🖼️ Diagram", type=["png", "jpg"])
            if up_img:
                st.session_state.img_data = Image.open(up_img)
                st.success("Image Saved!")
                
            yt_link = st.text_input("📺 YouTube Link")
            if yt_link:
                try:
                    video_id = yt_link.split("v=")[1][:11]
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    st.session_state.context_text = " ".join([t['text'] for t in transcript])
                    st.success("Video Subtitles Saved!")
                except:
                    st.error("Video load nahi hui.")

    with chat_col:
        prompt = st.chat_input("Type a question...")
        voice_input = st.audio_input("Or send a voice note:")

    user_query = prompt if prompt else ("Please answer my voice note" if voice_input else None)

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    sys_prompt = f"Answer in {pref_lang}. Context: {st.session_state.context_text[:4000]}\nHistory: {st.session_state.messages[-3:]}\nQuery: {user_query}"
                    
                    if st.session_state.img_data:
                        response = model.generate_content([sys_prompt, st.session_state.img_data])
                    else:
                        response = model.generate_content(sys_prompt)
                        
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"⚠️ Asli Error: {e}")
    
