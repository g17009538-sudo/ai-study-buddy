import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import datetime

# --- 1. ASTRA ULTRA-MODERN MASTERPIECE CSS & CONFIG ---
st.set_page_config(page_title="VeDA - Astra Pro Engine", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    .stApp { 
        background-color: #0b0f19; 
        color: #f8fafc; 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
    }
    [data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Astra Grid & Card Styling */
    .astra-card { 
        background: #131b2e; 
        border: 1px solid #1f2937;
        padding: 22px; 
        border-radius: 20px; 
        margin-bottom: 16px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .hero-title {
        font-weight: 700;
        font-size: 2rem;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    
    /* Custom Grid Layout Fix for Mobile */
    .row-widget { display: flex; gap: 10px; }
</style>
""", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception:
    st.error("⚠️ API key missing in Streamlit Secrets.")
    st.stop()

# --- 2. ROBUST SESSION STATE ENGINE ---
default_states = {
    "nav_tab": "Ask",
    "messages": [{"role": "assistant", "content": "Hello Gourav, welcome! 👋 I am VeDA, your dedicated AI academic mentor."}],
    "wizard_step": 1, 
    "exam_sub": "", 
    "exam_date": datetime.date.today(), 
    "target_score": 85,
    "edu_level": "Secondary stage (grades 9-12)",
    "grade": "10. grade",
    "strategy_plan": "", 
    "context_text": "", 
    "flashcard_data": [], 
    "quiz_data": None
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

def change_step(step): st.session_state.wizard_step = step
def set_subject(sub): 
    st.session_state.exam_sub = sub
    st.session_state.wizard_step = 2

active_tab = st.session_state.nav_tab

# ==========================================
# --- TAB 1: ASK (NEURAL CHAT WORKSPACE) ---
# ==========================================
if active_tab == "Ask":
    st.markdown('<p class="hero-title">Hello Gourav, welcome! 👋</p>', unsafe_allow_html=True)
    
    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    st.markdown("---")
    
    # Bottom Action Row matching Astra video
    col_a1, col_a2, col_a3 = st.columns([1, 1, 4])
    with col_a1:
        with st.popover("➕"):
            up_pdf = st.file_uploader("Upload PDF File", type="pdf")
            if up_pdf:
                try:
                    reader = PyPDF2.PdfReader(up_pdf)
                    raw_text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
                    st.session_state.context_text = raw_text[:4000]
                    st.success("PDF knowledge indexed successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
    with col_a2:
        up_img = st.file_uploader("📷", type=["png", "jpg"], label_visibility="collapsed")
        if up_img:
            st.session_state.img_data = Image.open(up_img)
            st.success("Visual attached!")
            
    user_query = st.chat_input("Ask, speak, or send a file...")

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("VeDA is thinking..."):
                try:
                    sys_prompt = f"You are VeDA, an elite AI tutor. Context: {st.session_state.context_text[:4000]}\nQuery: {user_query}"
                    response = model.generate_content([sys_prompt, st.session_state.img_data]) if st.session_state.img_data else model.generate_content(sys_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")

# ==========================================
# --- TAB 2: EXAMS (ASTRA PREP WIZARD) ---
# ==========================================
elif active_tab == "Exams":
    
    # Step 1: Subject Selection (Grid style)
    if st.session_state.wizard_step == 1:
        st.markdown('<div class="astra-card">', unsafe_allow_html=True)
        st.markdown("### Choose a subject")
        
        custom_sub = st.text_input("Type your subject...", placeholder="e.g. Advanced Calculus")
        if st.button("➕ Add custom subject") and custom_sub:
            set_subject(custom_sub)
            st.rerun()
            
        st.markdown("<p style='color: #94a3b8; font-size: 0.85rem; margin-top: 15px;'>General subjects</p>", unsafe_allow_html=True)
        
        # Grid arrangement for subjects
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📐 Math"): set_subject("Math")
            if st.button("🧪 Chemistry"): set_subject("Chemistry")
            if st.button("📚 English"): set_subject("English")
            if st.button("🇪🇸 Spanish"): set_subject("Spanish")
            if st.button("🧬 Biology"): set_subject("Biology")
            if st.button("📜 History"): set_subject("History")
        with col2:
            if st.button("💡 Physics"): set_subject("Physics")
            if st.button("💻 Computer Science"): set_subject("Computer Science")
            if st.button("🇩🇪 German"): set_subject("German")
            if st.button("🇫🇷 French"): set_subject("French")
            if st.button("🗺️ Geography"): set_subject("Geography")
            if st.button("📈 Economics"): set_subject("Economics")
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 2: Exam Timeline Date Selection
    elif st.session_state.wizard_step == 2:
        st.markdown('<div class="astra-card">', unsafe_allow_html=True)
        st.markdown(f"### When is your {st.session_state.exam_sub} exam?")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("🚨 Tomorrow"):
                st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=1)
                change_step(3)
                st.rerun()
            if st.button("⚡ In 3 days"):
                st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=3)
                change_step(3)
                st.rerun()
        with col_t2:
            if st.button("⚡ In 2 days"):
                st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=2)
                change_step(3)
                st.rerun()
            if st.button("📅 Next few days"):
                st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=7)
                change_step(3)
                st.rerun()
                
        st.markdown("<p style='text-align: center; color: #94a3b8; margin: 15px 0;'>Or</p>", unsafe_allow_html=True)
        st.session_state.exam_date = st.date_input("Pick a date", min_value=datetime.date.today())
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Back"): change_step(1)
        with c2:
            if st.button("Continue ➡️", type="primary"): change_step(3)
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 3: Target Score Mastery Goal Slider
    elif st.session_state.wizard_step == 3:
        st.markdown('<div class="astra-card">', unsafe_allow_html=True)
        st.markdown("### What is your target score?")
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Mastery goal percentage</p>", unsafe_allow_html=True)
        
        st.session_state.target_score = st.slider("Target Score", 50, 100, 85, label_visibility="collapsed")
        st.markdown(f"<h1 style='text-align: center; color: #f48024; font-size: 3.5rem;'>{st.session_state.target_score}%</h1>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Back"): change_step(2)
        with c2:
            if st.button("Continue ➡️", type="primary"): change_step(4)
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 4: School Details & Grade Selection
    elif st.session_state.wizard_step == 4:
        st.markdown('<div class="astra-card">', unsafe_allow_html=True)
        st.markdown("### Confirm your school details")
        st.text_input("Search school", placeholder="Enter institution name...")
        
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem; margin-top: 10px;'>Which level of education are you in?</p>", unsafe_allow_html=True)
        edu_options = [
            "Foundational stage - primary grades 1-2",
            "Preparatory stage (grades 3-5)",
            "Middle stage (grades 6-8)",
            "Secondary stage (grades 9-12)",
            "Vocational / skill education",
            "University / higher education"
        ]
        st.session_state.edu_level = st.selectbox("Education level", edu_options, label_visibility="collapsed")
        
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem; margin-top: 10px;'>Which grade are you in?</p>", unsafe_allow_html=True)
        grade_options = ["9. grade", "10. grade", "11. grade", "12. grade"]
        st.session_state.grade = st.selectbox("Grade", grade_options, label_visibility="collapsed")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Back"): change_step(3)
        with c2:
            if st.button("Continue to Upload ➡️", type="primary"): change_step(5)
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 5: Upload Notes & Generate Blueprint
    elif st.session_state.wizard_step == 5:
        st.markdown('<div class="astra-card">', unsafe_allow_html=True)
        st.markdown("### Upload your study notes")
        up_pdf = st.file_uploader("Upload PDF material", type="pdf")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Back"): change_step(4)
        with c2:
            if st.button("🚀 Generate Blueprint", type="primary"):
                if up_pdf:
                    try:
                        reader = PyPDF2.PdfReader(up_pdf)
                        raw_text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
                        st.session_state.context_text = raw_text[:4000] if raw_text else "General curriculum material."
                    except Exception as e:
                        st.error(f"Error: {e}")
                
                with st.spinner("VeDA AI is constructing your master blueprint..."):
                    prompt = f"Act as an elite academic director. Create a high-impact study strategy for {st.session_state.exam_sub} targeting {st.session_state.target_score}%. Grade: {st.session_state.grade}. Context: {st.session_state.context_text}. Provide structural headings: 'Core Focus Pillars', 'Daily Execution Rhythm', and 'Key Formulas'."
                    response = model.generate_content(prompt)
                    st.session_state.strategy_plan = response.text
                    st.session_state.wizard_step = 6
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 6: Strategy Dashboard, Flashcards & Quiz
    elif st.session_state.wizard_step == 6:
        st.markdown(f"### 📊 Master Blueprint: {st.session_state.exam_sub}")
        st.markdown(f'<div class="astra-card">{st.session_state.strategy_plan}</div>', unsafe_allow_html=True)
        
        if st.button("🗂️ Learn with Flashcards"):
            with st.spinner("Synthesizing flashcards..."):
                res = model.generate_content(f"Create 3 Q&A flashcards from: {st.session_state.context_text}. Format strictly as Q: [Question] | A: [Answer] separated by lines.").text
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
                        
            if st.button("❓ Ready for Quiz", type="primary"):
                with st.spinner("Generating evaluation..."):
                    quiz_prompt = f"Create 1 multiple-choice question from: {st.session_state.context_text}. Format as:\nQuestion: [Text]\nA) [Opt1]\nB) [Opt2]\nC) [Opt3]\nCorrect: [A, B, or C]"
                    st.session_state.quiz_data = model.generate_content(quiz_prompt).text
                    st.rerun()

        if st.session_state.quiz_data:
            st.markdown("---")
            st.markdown("#### 🧠 Knowledge Check Evaluation")
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
            st.session_state.wizard_step = 1
            st.session_state.nav_tab = "Ask"
            st.rerun()

# ==========================================
# --- TAB 3: APPS (ECOSYSTEM TOOLS) ---
# ==========================================
elif active_tab == "Apps":
    st.markdown('<p class="hero-title">VeDA Ecosystem</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="astra-card">
        <h4>⚡ Formula Vault</h4>
        <p style="color: #94a3b8;">Quick reference sheets for formulas and key scientific constants.</p>
    </div>
    <div class="astra-card">
        <h4>⏱️ Pomodoro Focus Timer</h4>
        <p style="color: #94a3b8;">Optimized deep-work sessions for maximum memory retention.</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# --- BOTTOM DOCK NAVIGATION BAR ---
# ==========================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
c_d1, c_d2, c_d3 = st.columns(3)

with c_d1:
    if st.button("💬 Ask"):
        st.session_state.nav_tab = "Ask"
        st.rerun()
with c_d2:
    if st.button("🎯 Exams"):
        st.session_state.nav_tab = "Exams"
        st.rerun()
with c_d3:
    if st.button("📦 Apps"):
        st.session_state.nav_tab = "Apps"
        st.rerun()
    
