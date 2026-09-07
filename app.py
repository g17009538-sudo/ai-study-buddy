import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import datetime

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(page_title="VeDA - AI Study Tutor", page_icon="🎓", layout="centered")
st.markdown("""
<style>
    .stApp { background-color: #FEF5F0; color: #1E1E1E; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 2px solid #F48024; }
    .stButton>button { border-radius: 10px; border: 1.5px solid #F48024; color: #F48024; width: 100%; font-weight: 600; background-color: white; padding: 10px; }
    .stButton>button:hover { background-color: #F48024; color: white; }
    .veda-card { background-color: white; padding: 22px; border-radius: 12px; border-left: 6px solid #F48024; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .hero-container { text-align: center; padding: 20px 0; }
</style>
""", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception:
    st.error("⚠️ API key missing in Streamlit Secrets. Please configure it to power VeDA.")
    st.stop()

# --- 2. ROBUST SESSION STATE ENGINE ---
default_states = {
    "app_nav": "Home",
    "messages": [{"role": "assistant", "content": "Hello! I am **VeDA**, your advanced AI study companion. How can I empower your preparation today?"}],
    "wizard_step": 1, 
    "exam_sub": "", 
    "exam_date": datetime.date.today(), 
    "target_score": 85,
    "strategy_plan": "", 
    "context_text": "", 
    "img_data": None,
    "flashcard_data": [], 
    "quiz_data": None, 
    "quiz_selected": None
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

def navigate_to(page):
    st.session_state.app_nav = page

def change_step(step):
    st.session_state.wizard_step = step

def set_subject(sub):
    st.session_state.exam_sub = sub
    st.session_state.wizard_step = 2

def reset_veda_wizard():
    st.session_state.wizard_step = 1
    st.session_state.flashcard_data = []
    st.session_state.quiz_data = None
    st.session_state.strategy_plan = ""

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🎓 VeDA Control Hub")
    st.divider()
    if st.button("🏠 Main Dashboard"): navigate_to("Home")
    if st.button("📅 Exam Prep Wizard"): navigate_to("Wizard")
    if st.button("💬 Chat with VeDA"): navigate_to("Chat")
    st.divider()
    if st.button("🗑️ Reset Session Memory"):
        for k, v in default_states.items():
            st.session_state[k] = v
        st.rerun()

# --- 4. LANDING SCREEN (HOME) ---
if st.session_state.app_nav == "Home":
    st.markdown('<div class="hero-container"><h1>Meet <b>VeDA</b></h1><p>Your Next-Gen AI Learning & Exam Preparation Ecosystem</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📅 Exam Prep Mode")
        st.write("Step-by-step smart planner, AI strategy generation, interactive flashcards, and adaptive quizzes.")
        if st.button("Launch Wizard 🚀"):
            navigate_to("Wizard")
            st.rerun()
    with col2:
        st.markdown("### 💬 VeDA Assistant")
        st.write("Have an open discussion, upload complex diagrams, parse dense PDFs, or use voice notes.")
        if st.button("Open Chat 💬"):
            navigate_to("Chat")
            st.rerun()

# --- 5. EXAM PREP WIZARD MODE ---
elif st.session_state.app_nav == "Wizard":
    st.title("🎯 VeDA Exam Planner")
    
    # Step 1: Subject Selection
    if st.session_state.wizard_step == 1:
        st.subheader("Step 1: Choose Your Subject")
        c1, c2 = st.columns(2)
        c1.button("📐 Mathematics", on_click=set_subject, args=("Mathematics",))
        c2.button("💡 Physics", on_click=set_subject, args=("Physics",))
        c1.button("🧪 Chemistry", on_click=set_subject, args=("Chemistry",))
        c2.button("💻 Computer Science", on_click=set_subject, args=("Computer Science",))
        
        custom_sub = st.text_input("Or enter custom subject/exam name:")
        if st.button("Continue with Custom Subject") and custom_sub:
            set_subject(custom_sub)
            st.rerun()
            
    # Step 2: Exam Date
    elif st.session_state.wizard_step == 2:
        st.subheader(f"Step 2: When is your {st.session_state.exam_sub} exam?")
        st.session_state.exam_date = st.date_input("Select Target Date", min_value=datetime.date.today())
        c1, c2 = st.columns(2)
        c1.button("⬅️ Back", on_click=change_step, args=(1,))
        c2.button("Next Step ➡️", on_click=change_step, args=(3,))
        
    # Step 3: Target Score Slider
    elif st.session_state.wizard_step == 3:
        st.subheader("Step 3: Set Your Target Score")
        st.session_state.target_score = st.slider("Expected Achievement (%)", 0, 100, 85)
        c1, c2 = st.columns(2)
        c1.button("⬅️ Back", on_click=change_step, args=(2,))
        c2.button("Next Step ➡️", on_click=change_step, args=(4,))
        
    # Step 4: Material Upload & Strategy Generation
    elif st.session_state.wizard_step == 4:
        st.subheader("Step 4: Upload Reference Material")
        up_pdf = st.file_uploader("Upload Syllabus or Chapter Notes (PDF)", type="pdf")
        
        c1, c2 = st.columns(2)
        c1.button("⬅️ Back", on_click=change_step, args=(3,))
        
        if c2.button("🚀 Generate Master Strategy"):
            if up_pdf:
                st.session_state.context_text = "".join(page.extract_text() for page in PyPDF2.PdfReader(up_pdf).pages if page.extract_text())
            
            days_left = (st.session_state.exam_date - datetime.date.today()).days
            with st.spinner("VeDA is analyzing your material and drafting a comprehensive strategy..."):
                prompt = f"Act as an elite academic strategist. Create a powerful study strategy for {st.session_state.exam_sub} in {days_left} days aiming for {st.session_state.target_score}%. Context: {st.session_state.context_text[:4000]}. Format with clear headings for 'High-Weightage Topics', 'Study Methodology', and 'Time Management'."
                st.session_state.strategy_plan = model.generate_content(prompt).text
                st.session_state.wizard_step = 5
                st.rerun()

    # Step 5: Dashboard, Flashcards, and Quiz Integration
    elif st.session_state.wizard_step == 5:
        st.subheader(f"📊 VeDA Master Strategy: {st.session_state.exam_sub}")
        st.markdown(f'<div class="veda-card">{st.session_state.strategy_plan}</div>', unsafe_allow_html=True)
        
        col_f, col_q = st.columns(2)
        if col_f.button("🗂️ Generate Interactive Flashcards"):
            with st.spinner("VeDA is building targeted flashcards..."):
                fc_prompt = f"Create 3 high-yield Q&A flashcards from this text: {st.session_state.context_text[:3000]}. Format strictly as Q: [Question] | A: [Answer] separated by newline."
                res = model.generate_content(fc_prompt).text
                st.session_state.flashcard_data = res.split('\n')
                st.rerun()
                
        # Render Flashcards if available
        if st.session_state.flashcard_data:
            st.write("---")
            st.subheader("💡 Core Concept Flashcards")
            for card in st.session_state.flashcard_data:
                if "|" in card:
                    parts = card.split("|")
                    q = parts[0].replace("Q:", "").strip()
                    a = parts[1].replace("A:", "").strip()
                    with st.expander(f"📌 {q}"):
                        st.success(f"Answer: {a}")
                        
            if st.button("❓ Ready for Adaptive Quiz"):
                with st.spinner("VeDA is formulating an evaluation test..."):
                    quiz_prompt = f"Create 1 multiple choice question based on: {st.session_state.context_text[:3000]}. Format as:\nQuestion: [Text]\nA) [Opt1]\nB) [Opt2]\nC) [Opt3]\nCorrect: [A, B, or C]"
                    st.session_state.quiz_data = model.generate_content(quiz_prompt).text
                    st.rerun()

        # Render Quiz if available
        if st.session_state.quiz_data:
            st.write("---")
            st.subheader("🧠 Knowledge Check Evaluation")
            lines = st.session_state.quiz_data.split('\n')
            q_text = next((l for l in lines if l.startswith("Question:")), "Question")
            correct_key = next((l for l in lines if l.startswith("Correct:")), "").replace("Correct:", "").strip()
            
            st.write(f"**{q_text}**")
            options = [l for l in lines if l.startswith("A)") or l.startswith("B)") or l.startswith("C)") ]
            
            for opt in options:
                opt_letter = opt[0]
                if st.button(opt, key=f"opt_{opt_letter}"):
                    if opt_letter == correct_key:
                        st.success("✅ Correct! Brilliant understanding of the concept.")
                    else:
                        st.error(f"❌ Incorrect. The correct option is {correct_key}.")
                        
        st.write("---")
        if st.button("🏠 Restart Planner"):
            reset_veda_wizard()
            navigate_to("Home")
            st.rerun()

# --- 6. CHAT WITH VEDA MODE ---
elif st.session_state.app_nav == "Chat":
    st.title("💬 VeDA Intelligent Assistant")
    
    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Clean Upload Expander
    with st.expander("📎 Attach Study Document, Image, or Voice Note"):
        c1, c2 = st.columns(2)
        with c1:
            up_pdf = st.file_uploader("Upload PDF Context", type="pdf")
            if up_pdf:
                st.session_state.context_text = "".join(page.extract_text() for page in PyPDF2.PdfReader(up_pdf).pages if page.extract_text())
                st.success("PDF Context Loaded into VeDA Memory!")
        with c2:
            up_img = st.file_uploader("Upload Diagram / Image", type=["png", "jpg"])
            if up_img:
                st.session_state.img_data = Image.open(up_img)
                st.success("Image Loaded into VeDA Memory!")
        voice_note = st.audio_input("Record Voice Query")

    # Chat Input Box
    prompt = st.chat_input("Ask VeDA anything...")
    user_input = prompt if prompt else ("Please address my uploaded voice note" if voice_note else None)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("VeDA is thinking..."):
                try:
                    sys_prompt = f"You are VeDA, an elite AI study tutor. Answer with extreme clarity and precision. Context: {st.session_state.context_text[:4000]}\nUser Query: {user_input}"
                    response = model.generate_content([sys_prompt, st.session_state.img_data]) if st.session_state.img_data else model.generate_content(sys_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"VeDA encountered an error: {e}")
                    
