import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import datetime

# --- 1. ASTRA-INSPIRED MOBILE APP CONFIG & STYLING ---
st.set_page_config(page_title="VeDA - Astra Edition", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    /* Astra Deep Dark Theme */
    .stApp { 
        background-color: #0b0f19; 
        color: #f8fafc; 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
    }
    [data-testid="stSidebar"] { 
        background-color: #07090e; 
        border-right: 1px solid #1f2937; 
    }
    /* Astra Rounded Dark Cards & Buttons */
    .stButton>button { 
        border-radius: 16px; 
        border: 1px solid #1f2937; 
        color: #ffffff; 
        background-color: #131b2e;
        width: 100%; 
        font-weight: 500; 
        padding: 14px; 
        text-align: left;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover { 
        border-color: #f48024;
        background-color: #1e293b;
    }
    /* Primary Action Buttons */
    .primary-btn button {
        background: linear-gradient(135deg, #f48024 0%, #ea580c 100%) !important;
        border: none !important;
        text-align: center !important;
        font-weight: 700 !important;
    }
    .astra-card { 
        background: #131b2e; 
        border: 1px solid #1f2937;
        padding: 20px; 
        border-radius: 20px; 
        margin-bottom: 15px; 
    }
    .hero-title {
        font-weight: 700;
        font-size: 2rem;
        color: #ffffff;
    }
    /* Hide default Streamlit branding for clean mobile look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception:
    st.error("⚠️ API key missing in Streamlit Secrets.")
    st.stop()

# --- 2. ADVANCED SESSION STATE ---
default_states = {
    "app_nav": "Home",
    "messages": [{"role": "assistant", "content": "Hello Gourav, welcome! 👋 I am VeDA, your AI academic mentor."}],
    "wizard_step": 1, 
    "exam_sub": "", 
    "exam_timing": "",
    "exam_date": datetime.date.today(), 
    "target_score": 85,
    "edu_level": "",
    "grade": "",
    "strategy_plan": "", 
    "context_text": "", 
    "flashcard_data": [], 
    "quiz_data": None
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

def navigate_to(page): st.session_state.app_nav = page
def change_step(step): st.session_state.wizard_step = step
def set_subject(sub): 
    st.session_state.exam_sub = sub
    st.session_state.wizard_step = 2

# --- 3. BOTTOM MOBILE NAVIGATION BAR SIMULATION ---
with st.sidebar:
    st.markdown("### 🧭 **VeDA Navigation**")
    if st.button("🏠 Home / Dashboard"): navigate_to("Home")
    if st.button("🎯 Exam Prep Wizard"): navigate_to("Wizard")
    if st.button("💬 VeDA Chat"): navigate_to("Chat")
    st.divider()
    if st.button("🔄 Reset App State"):
        for k, v in default_states.items(): st.session_state[k] = v
        st.rerun()

# --- 4. HOME SCREEN (ASTRA STYLE) ---
if st.session_state.app_nav == "Home":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; font-size: 0.9rem;">🔥 BACK TO SCHOOL DEAL: Save 67% with VeDA Plus</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Hello Gourav, welcome! 👋</p>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hero Card matching Astra's "Prepare for your Exams with AI"
    st.markdown("""
    <div class="astra-card" style="text-align: center; background: radial-gradient(circle, #1e293b 0%, #131b2e 100%);">
        <h3>🎓 Prepare for your Exams with AI</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">Generate intelligent roadmaps, master concepts via active recall, and test yourself.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ Create new exam", type="primary"):
        st.session_state.wizard_step = 1
        navigate_to("Wizard")
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💬 Jump to Neural Chat"):
        navigate_to("Chat")
        st.rerun()

# --- 5. EXAM PREP WIZARD (EXACT ASTRA FLOW) ---
elif st.session_state.app_nav == "Wizard":
    
    # Step 1: Choose a subject (Grid matching video)
    if st.session_state.wizard_step == 1:
        st.markdown("### Choose a subject")
        custom_sub = st.text_input("Type your subject", placeholder="Search subject...")
        
        if st.button("➕ Add your subject") and custom_sub:
            set_subject(custom_sub)
            st.rerun()
            
        st.markdown("<p style='color: #94a3b8; font-size: 0.85rem; margin-top: 10px;'>General subjects</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📐 Math"): set_subject("Math")
            if st.button("🧪 Chemistry"): set_subject("Chemistry")
            if st.button("📚 English"): set_subject("English")
            if st.button("🌍 Spanish"): set_subject("Spanish")
            if st.button("🧬 Biology"): set_subject("Biology")
            if st.button("📜 History"): set_subject("History")
        with col2:
            if st.button("💡 Physics"): set_subject("Physics")
            if st.button("💻 Computer Science"): set_subject("Computer Science")
            if st.button("🇩🇪 German"): set_subject("German")
            if st.button("🇫🇷 French"): set_subject("French")
            if st.button("🗺️ Geography"): set_subject("Geography")
            if st.button("🏛️ Economics"): set_subject("Economics")

    # Step 2: When is your exam? (Timeline options matching video)
    elif st.session_state.wizard_step == 2:
        st.markdown(f"### When is your {st.session_state.exam_sub} exam?")
        
        if st.button("🚨 Tomorrow"):
            st.session_state.exam_timing = "Tomorrow"
            st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=1)
            change_step(3)
            st.rerun()
        if st.button("⚡ In 2 days"):
            st.session_state.exam_timing = "In 2 days"
            st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=2)
            change_step(3)
            st.rerun()
        if st.button("⚡ In 3 days"):
            st.session_state.exam_timing = "In 3 days"
            st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=3)
            change_step(3)
            st.rerun()
        if st.button("📅 Next few days"):
            st.session_state.exam_timing = "Next few days"
            st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=7)
            change_step(3)
            st.rerun()
            
        st.markdown("<p style='text-align: center; color: #94a3b8;'>Or</p>", unsafe_allow_html=True)
        st.session_state.exam_date = st.date_input("Pick a date", min_value=datetime.date.today())
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"): change_step(1)
        with col2:
            if st.button("Continue", type="primary"): change_step(3)

    # Step 3: Target Score / Mastery Goal Slider
    elif st.session_state.wizard_step == 3:
        st.markdown("### What is your target score?")
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Mastery goal percentage</p>", unsafe_allow_html=True)
        
        st.session_state.target_score = st.slider("Target Score", 50, 100, 85, label_visibility="collapsed")
        st.markdown(f"<h1 style='text-align: center; color: #f48024;'>{st.session_state.target_score}%</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"): change_step(2)
        with col2:
            if st.button("Continue", type="primary"): change_step(4)

    # Step 4: School Details & Education Level
    elif st.session_state.wizard_step == 4:
        st.markdown("### Confirm your school details")
        st.text_input("Search school", placeholder="Type school name...")
        
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Which level of education are you in?</p>", unsafe_allow_html=True)
        edu_options = [
            "Foundational stage - primary grades 1-2",
            "Preparatory stage (grades 3-5)",
            "Middle stage (grades 6-8)",
            "Secondary stage (grades 9-12)",
            "Vocational / skill education",
            "University / higher education"
        ]
        selected_edu = st.radio("Education Level", edu_options, label_visibility="collapsed")
        st.session_state.edu_level = selected_edu
        
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Which grade are you in?</p>", unsafe_allow_html=True)
        grade_options = ["9. grade", "10. grade", "11. grade", "12. grade"]
        selected_grade = st.radio("Grade", grade_options, label_visibility="collapsed")
        st.session_state.grade = selected_grade
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"): change_step(3)
        with col2:
            if st.button("Continue to Upload", type="primary"): change_step(5)

    # Step 5: Upload Notes & Generate Master Strategy
    elif st.session_state.wizard_step == 5:
        st.markdown("### Upload your study notes")
        up_pdf = st.file_uploader("Upload PDF material", type="pdf")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"): change_step(4)
        with col2:
            if st.button("🚀 Generate Blueprint", type="primary"):
                if up_pdf:
                    try:
                        reader = PyPDF2.PdfReader(up_pdf)
                        raw_text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
                        st.session_state.context_text = raw_text[:3000] if raw_text else "General curriculum notes."
                    except Exception as e:
                        st.error(f"Error reading PDF: {e}")
                
                with st.spinner("VeDA AI is compiling your master strategy..."):
                    prompt = f"Act as an elite academic director. Create a high-impact study strategy for {st.session_state.exam_sub} targeting {st.session_state.target_score}%. Grade level: {st.session_state.grade}. Context: {st.session_state.context_text}. Provide structural headings: 'Core Focus Pillars', 'Daily Execution Rhythm', and 'Key Formulas'."
                    response = model.generate_content(prompt)
                    st.session_state.strategy_plan = response.text
                    st.session_state.wizard_step = 6
                    st.rerun()

    # Step 6: Strategy Dashboard, Flashcards & Quiz
    elif st.session_state.wizard_step == 6:
        st.markdown(f"### 📊 Master Blueprint: {st.session_state.exam_sub}")
        st.markdown(f'<div class="astra-card">{st.session_state.strategy_plan}</div>', unsafe_allow_html=True)
        
        if st.button("🗂️ Generate Smart Flashcards"):
            with st.spinner("Synthesizing flashcards..."):
                fc_prompt = f"Extract 3 high-yield Q&A pairs from: {st.session_state.context_text}. Format strictly as Q: [Question] | A: [Answer] separated by lines."
                res = model.generate_content(fc_prompt).text
                st.session_state.flashcard_data = res.split('\n')
                st.rerun()
                
        if st.session_state.flashcard_data:
            st.markdown("---")
            st.markdown("#### 💡 Interactive Memory Cards")
            for card in st.session_state.flashcard_data:
                if "|" in card:
                    parts = card.split("|")
                    q = parts[0].replace("Q:", "").strip()
                    a = parts[1].replace("A:", "").strip()
                    with st.expander(f"📌 {q}"):
                        st.success(f"**Answer:** {a}")
                        
            if st.button("❓ Initialize Adaptive Quiz"):
                with st.spinner("Generating evaluation..."):
                    quiz_prompt = f"Create a multiple-choice question from: {st.session_state.context_text}. Format as:\nQuestion: [Text]\nA) [Opt1]\nB) [Opt2]\nC) [Opt3]\nCorrect: [A, B, or C]"
                    st.session_state.quiz_data = model.generate_content(quiz_prompt).text
                    st.rerun()

        if st.session_state.quiz_data:
            st.markdown("---")
            st.markdown("#### 🧠 Knowledge Check")
            lines = st.session_state.quiz_data.split('\n')
            q_text = next((l for l in lines if l.startswith("Question:")), "Question")
            correct_key = next((l for l in lines if l.startswith("Correct:")), "").replace("Correct:", "").strip()
            
            st.markdown(f"**{q_text}**")
            options = [l for l in lines if l.startswith("A)") or l.startswith("B)") or l.startswith("C)")]
            
            for opt in options:
                opt_letter = opt[0]
                if st.button(opt, key=f"quiz_opt_{opt_letter}"):
                    if opt_letter == correct_key:
                        st.success("✅ Correct! Absolute precision.")
                    else:
                        st.error(f"❌ Incorrect. The correct key is {correct_key}.")
                        
        st.markdown("---")
        if st.button("🏠 Return to Home"):
            navigate_to("Home")
            st.rerun()

# --- 6. NEURAL CHAT WITH VEDA ---
elif st.session_state.app_nav == "Chat":
    st.markdown("### 💬 VeDA Neural Workspace")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    with st.expander("📎 Ingest Context (PDF / Image)"):
        up_pdf = st.file_uploader("Document Ingestion (.PDF)", type="pdf")
        if up_pdf:
            try:
                reader = PyPDF2.PdfReader(up_pdf)
                raw_text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
                st.session_state.context_text = raw_text[:2500] if raw_text else ""
                st.success("PDF knowledge indexed successfully.")
            except Exception as e:
                st.error(f"Error: {e}")

    prompt = st.chat_input("Ask VeDA...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("VeDA is thinking..."):
                try:
                    sys_prompt = f"You are VeDA, an elite AI educational architecture. Context: {st.session_state.context_text[:3000]}\nQuery: {prompt}"
                    response = model.generate_content(sys_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")
                    
