import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import datetime
from youtube_transcript_api import YouTubeTranscriptApi

# UI & Custom Theme
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
    st.error("⚠️ API key missing.")
    st.stop()

# Session States
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Main tumhara AI Tutor hoon. 😊"}]
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
if "exam_sub" not in st.session_state:
    st.session_state.exam_sub = ""
if "exam_date" not in st.session_state:
    st.session_state.exam_date = datetime.date.today()
if "target_score" not in st.session_state:
    st.session_state.target_score = 80
if "study_plan" not in st.session_state:
    st.session_state.study_plan = None
if "context_text" not in st.session_state:
    st.session_state.context_text = ""
if "img_data" not in st.session_state:
    st.session_state.img_data = None

def next_step(step):
    st.session_state.wizard_step = step

def set_subject(sub):
    st.session_state.exam_sub = sub
    st.session_state.wizard_step = 2

# Sidebar Menu
with st.sidebar:
    app_mode = st.radio("Navigation", ["💬 Chat & Tools", "📅 Exam Prep Wizard"])
    st.divider()
    
    st.subheader("📺 Add YouTube Video")
    yt_link = st.text_input("Paste YouTube Link")
    if st.button("Process Video"):
        try:
            video_id = yt_link.split("v=")[1][:11]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            st.session_state.context_text = " ".join([t['text'] for t in transcript])
            st.success("Video processed!")
        except:
            st.error("Invalid link.")

# ----------------- MODE 1: EXAM PREP WIZARD -----------------
if app_mode == "📅 Exam Prep Wizard":
    st.title("Interactive Exam Planner")
    
    # Step 1: Subject
    if st.session_state.wizard_step == 1:
        st.subheader("Step 1: Choose a subject")
        col1, col2 = st.columns(2)
        with col1:
            st.button("📐 Math", use_container_width=True, on_click=set_subject, args=("Math",))
            st.button("🧪 Chemistry", use_container_width=True, on_click=set_subject, args=("Chemistry",))
        with col2:
            st.button("💡 Physics", use_container_width=True, on_click=set_subject, args=("Physics",))
            st.button("💻 Computer Science", use_container_width=True, on_click=set_subject, args=("Computer Science",))
        
        custom_sub = st.text_input("Or type your subject:")
        if st.button("Continue", type="primary"):
            if custom_sub:
                set_subject(custom_sub)
    
    # Step 2: Date
    elif st.session_state.wizard_step == 2:
        st.subheader(f"Step 2: When is your {st.session_state.exam_sub} exam?")
        st.session_state.exam_date = st.date_input("Select Date", min_value=datetime.date.today())
        col1, col2 = st.columns([1, 10])
        col1.button("Back", on_click=next_step, args=(1,))
        col2.button("Next", on_click=next_step, args=(3,))
        
    # Step 3: Target Score
    elif st.session_state.wizard_step == 3:
        st.subheader("Step 3: What is your target score?")
        st.session_state.target_score = st.slider("Expected Marks (%)", 0, 100, 80)
        col1, col2 = st.columns([1, 10])
        col1.button("Back", on_click=next_step, args=(2,))
        col2.button("Next", on_click=next_step, args=(4,))
        
    # Step 4: Upload & Generate
    elif st.session_state.wizard_step == 4:
        st.subheader("Step 4: Add your study material")
        up_pdf = st.file_uploader("Upload Notes (PDF)", type="pdf")
        
        col1, col2 = st.columns([1, 10])
        col1.button("Back", on_click=next_step, args=(3,))
        
        if col2.button("🚀 Create Path"):
            if up_pdf:
                st.session_state.context_text = "".join(page.extract_text() for page in PyPDF2.PdfReader(up_pdf).pages if page.extract_text())
            
            days_left = (st.session_state.exam_date - datetime.date.today()).days
            with st.spinner("Analyzing material... Creating path..."):
                prompt = f"Create a day-by-day study plan for {st.session_state.exam_sub} exam in {days_left} days. Target: {st.session_state.target_score}%. Format EXACTLY like this: 'DAY 1: Topic Name - Details|DAY 2: Topic Name - Details'."
                response = model.generate_content(prompt)
                st.session_state.study_plan = response.text.split('|')
                st.session_state.wizard_step = 5
                st.rerun()
                
    # Step 5: Dashboard Boxes
    elif st.session_state.wizard_step == 5:
        st.subheader(f"🗓️ Your {st.session_state.exam_sub} Study Plan")
        for i, day_task in enumerate(st.session_state.study_plan):
            if day_task.strip():
                st.markdown(f'<div class="study-box">{day_task}</div>', unsafe_allow_html=True)
                st.checkbox(f"✅ Mark Day {i+1} as Done", key=f"day_{i}")
        if st.button("🔄 Restart Planner"):
            st.session_state.wizard_step = 1
            st.rerun()

# ----------------- MODE 2: CHAT & TOOLS -----------------
elif app_mode == "💬 Chat & Tools":
    st.title("🎓 Smart AI Study Tutor")
    
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    st.write("") # Spacing
    
    # Quick Action Row right above Chat Input
    col1, col2, col3 = st.columns([1, 2, 7])
    with col1:
        with st.popover("➕ Upload"):
            up_pdf = st.file_uploader("📝 PDF Notes", type="pdf")
            if up_pdf:
                st.session_state.context_text = "".join(page.extract_text() for page in PyPDF2.PdfReader(up_pdf).pages if page.extract_text())
                st.success("PDF Saved!")
            up_img = st.file_uploader("🖼️ Diagram", type=["png", "jpg"])
            if up_img:
                st.session_state.img_data = Image.open(up_img)
                st.success("Image Saved!")
    with col2:
        voice_input = st.audio_input("🎤 Voice")
    
    # Text Chat Input
    prompt = st.chat_input("Ask Gemini...")
    user_query = prompt if prompt else ("Please answer my voice note" if voice_input else None)

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    sys_prompt = f"Answer clearly. Context: {st.session_state.context_text[:4000]}\nQuery: {user_query}"
                    if st.session_state.img_data:
                        response = model.generate_content([sys_prompt, st.session_state.img_data])
                    else:
                        response = model.generate_content(sys_prompt)
                        
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
                    
