import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import datetime
from youtube_transcript_api import YouTubeTranscriptApi

# App UI & Custom Theme
st.set_page_config(page_title="AI Study Tutor", page_icon="🎓", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #FEF5F0; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 2px solid #F48024; }
    .stButton>button { border-radius: 8px; border: 1px solid #F48024; color: #F48024; width: 100%; }
    .stButton>button:hover { background-color: #F48024; color: white; }
    .strategy-box { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #F48024; margin-bottom: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .success-text { color: #28a745; font-weight: bold; }
    .error-text { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception:
    st.error("⚠️ API key missing in Streamlit Secrets.")
    st.stop()

# Session State Initialization
default_states = {
    "messages": [{"role": "assistant", "content": "Welcome to your AI Study Tutor. How can I help you prepare today?"}],
    "wizard_step": 1,
    "exam_sub": "",
    "exam_date": datetime.date.today(),
    "target_score": 80,
    "strategy_plan": "",
    "context_text": "",
    "img_data": None,
    "flashcards_active": False,
    "quiz_active": False,
    "quiz_feedback": ""
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

def change_step(step):
    st.session_state.wizard_step = step

def set_subject(sub):
    st.session_state.exam_sub = sub
    st.session_state.wizard_step = 2

def reset_wizard():
    st.session_state.wizard_step = 1
    st.session_state.flashcards_active = False
    st.session_state.quiz_active = False
    st.session_state.strategy_plan = ""

# Sidebar
with st.sidebar:
    app_mode = st.radio("Navigation", ["💬 Chat & Tools", "📅 Exam Prep Mode"])
    st.divider()
    st.subheader("📺 Add YouTube Video")
    yt_link = st.text_input("Paste YouTube Link")
    if st.button("Process Video"):
        try:
            video_id = yt_link.split("youtu.be/")[1].split("?")[0][:11] if "youtu.be/" in yt_link else yt_link.split("v=")[1].split("&")[0][:11]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            st.session_state.context_text = " ".join([t['text'] for t in transcript])
            st.success("Video processed successfully!")
        except Exception:
            st.error("Could not extract subtitles. Ensure the video has closed captions.")

# ----------------- MODE 1: EXAM PREP WIZARD -----------------
if app_mode == "📅 Exam Prep Mode":
    st.title("Interactive Exam Planner")
    
    # Step 1: Subject Selection
    if st.session_state.wizard_step == 1:
        st.subheader("Step 1: Choose a subject")
        col1, col2 = st.columns(2)
        with col1:
            st.button("📐 Mathematics", on_click=set_subject, args=("Mathematics",))
            st.button("🧪 Chemistry", on_click=set_subject, args=("Chemistry",))
        with col2:
            st.button("💡 Physics", on_click=set_subject, args=("Physics",))
            st.button("💻 Computer Science", on_click=set_subject, args=("Computer Science",))
        
        custom_sub = st.text_input("Or type your subject manually:")
        if st.button("Continue"):
            if custom_sub:
                set_subject(custom_sub)
    
    # Step 2: Date Selection
    elif st.session_state.wizard_step == 2:
        st.subheader(f"Step 2: When is your {st.session_state.exam_sub} exam?")
        st.session_state.exam_date = st.date_input("Select Date", min_value=datetime.date.today())
        col1, col2 = st.columns([1, 1])
        col1.button("Back", on_click=change_step, args=(1,))
        col2.button("Next", on_click=change_step, args=(3,))
        
    # Step 3: Target Score Slider
    elif st.session_state.wizard_step == 3:
        st.subheader("Step 3: What is your target score?")
        st.session_state.target_score = st.slider("Expected Marks (%)", 0, 100, 80)
        col1, col2 = st.columns([1, 1])
        col1.button("Back", on_click=change_step, args=(2,))
        col2.button("Next", on_click=change_step, args=(4,))
        
    # Step 4: Upload & Generate Strategy
    elif st.session_state.wizard_step == 4:
        st.subheader("Step 4: Add your study material")
        up_pdf = st.file_uploader("Upload Notes (PDF)", type="pdf")
        
        col1, col2 = st.columns([1, 1])
        col1.button("Back", on_click=change_step, args=(3,))
        
        if col2.button("🚀 Generate Strategy"):
            if up_pdf:
                st.session_state.context_text = "".join(page.extract_text() for page in PyPDF2.PdfReader(up_pdf).pages if page.extract_text())
            days_left = (st.session_state.exam_date - datetime.date.today()).days
            
            with st.spinner("Analyzing material and building your master strategy..."):
                prompt = f"Act as an expert academic tutor. I have a {st.session_state.exam_sub} exam in {days_left} days. My target score is {st.session_state.target_score}%. Based on this material: {st.session_state.context_text[:5000]}, provide a highly detailed study strategy. Include 'Most Important Topics', 'How to study them', and 'Common mistakes to avoid'. Format it cleanly without markdown headers, just clear readable text."
                response = model.generate_content(prompt)
                st.session_state.strategy_plan = response.text
                st.session_state.wizard_step = 5
                st.rerun()

    # Step 5: Dashboard, Flashcards, and Quiz
    elif st.session_state.wizard_step == 5:
        st.subheader(f"📊 Your {st.session_state.exam_sub} Master Strategy")
        st.markdown(f'<div class="strategy-box">{st.session_state.strategy_plan}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        if col1.button("🗂️ Learn with Flashcards"):
            st.session_state.flashcards_active = True
            st.session_state.quiz_active = False
        if col2.button("❓ Ready for Quiz"):
            st.session_state.quiz_active = True
            st.session_state.flashcards_active = False

        if st.session_state.flashcards_active:
            st.divider()
            st.subheader("Interactive Flashcards")
            st.info("Click on a question to reveal the answer.")
            # Hardcoded example for structure; in production, you can generate this via AI
            with st.expander("Q: What is the primary focus of this topic?"):
                st.write("A: The core fundamentals outlined in the first chapter of your notes.")
            with st.expander("Q: What common mistake should be avoided?"):
                st.write("A: Skipping the foundational formulas before attempting complex problems.")
                
        if st.session_state.quiz_active:
            st.divider()
            st.subheader("Knowledge Check")
            quiz_q = "Based on your material, what is the most critical concept to review?"
            st.write(f"**{quiz_q}**")
            
            q_col1, q_col2 = st.columns(2)
            if q_col1.button("A) Fundamentals"):
                st.session_state.quiz_feedback = "<span class='success-text'>✅ Correct! Excellent retention.</span>"
            if q_col2.button("B) Advanced Theories"):
                st.session_state.quiz_feedback = "<span class='error-text'>❌ Incorrect. Review the basics first.</span>"
            
            if st.session_state.quiz_feedback:
                st.markdown(st.session_state.quiz_feedback, unsafe_allow_html=True)
                
            st.write("")
            qc1, qc2 = st.columns(2)
            qc1.button("🔄 Generate New Quiz")
            qc2.button("🏠 Return to Dashboard", on_click=reset_wizard)

# ----------------- MODE 2: CHAT & TOOLS -----------------
elif app_mode == "💬 Chat & Tools":
    st.title("🎓 Smart AI Study Tutor")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    st.write("") 
    
    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        with st.popover("➕"):
            up_pdf = st.file_uploader("📝 PDF", type="pdf", label_visibility="collapsed")
            if up_pdf:
                st.session_state.context_text = "".join(page.extract_text() for page in PyPDF2.PdfReader(up_pdf).pages if page.extract_text())
                st.success("Loaded!")
            up_img = st.file_uploader("🖼️ Image", type=["png", "jpg"], label_visibility="collapsed")
            if up_img:
                st.session_state.img_data = Image.open(up_img)
                st.success("Loaded!")
    with col2:
        voice_input = st.audio_input("🎤", label_visibility="collapsed")
    
    prompt = st.chat_input("Ask your tutor...")
    user_query = prompt if prompt else ("Please answer my voice note" if voice_input else None)

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    sys_prompt = f"Answer professionally. Context: {st.session_state.context_text[:4000]}\nQuery: {user_query}"
                    response = model.generate_content([sys_prompt, st.session_state.img_data]) if st.session_state.img_data else model.generate_content(sys_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")
                    
