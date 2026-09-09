mport streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import datetime

# --- 1. CONFIGURATION & ASTRA-GRADE STYLING ---
st.set_page_config(page_title="VeDA - Next-Gen AI Tutor", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    /* Global Theme & Glassmorphism Aesthetics */
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); 
        color: #f8fafc; 
        font-family: 'Inter', sans-serif; 
    }
    [data-testid="stSidebar"] { 
        background-color: #090d16; 
        border-right: 1px solid rgba(244, 128, 36, 0.3); 
    }
    .stButton>button { 
        border-radius: 12px; 
        border: 1px solid #f48024; 
        color: #ffffff; 
        background: linear-gradient(90deg, #f48024 0%, #ea580c 100%);
        width: 100%; 
        font-weight: 600; 
        padding: 10px; 
        box-shadow: 0 4px 12px rgba(244,128,36,0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(244,128,36,0.5);
    }
    .veda-card { 
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 24px; 
        border-radius: 16px; 
        border-left: 6px solid #f48024; 
        margin-bottom: 20px; 
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .hero-title {
        background: linear-gradient(90deg, #f48024, #fb923c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception:
    st.error("⚠️ API key missing in Streamlit Secrets. Please configure it to power VeDA.")
    st.stop()

# --- 2. ADVANCED SESSION STATE ENGINE ---
default_states = {
    "app_nav": "Home",
    "messages": [{"role": "assistant", "content": "Greetings! I am **VeDA**, your elite AI study mentor. Let's conquer your academic goals together."}],
    "wizard_step": 1, 
    "exam_sub": "", 
    "exam_date": datetime.date.today(), 
    "target_score": 90,
    "strategy_plan": "", 
    "context_text": "", 
    "img_data": None,
    "flashcard_data": [], 
    "quiz_data": None,
    "quiz_score": 0
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

def navigate_to(page): st.session_state.app_nav = page
def change_step(step): st.session_state.wizard_step = step
def set_subject(sub): 
    st.session_state.exam_sub = sub
    st.session_state.wizard_step = 2
def reset_veda():
    st.session_state.wizard_step = 1
    st.session_state.flashcard_data = []
    st.session_state.quiz_data = None
    st.session_state.strategy_plan = ""

# --- 3. IMMERSIVE SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### 🎓 **VeDA Control Center**")
    st.divider()
    if st.button("🏠 Command Hub"): navigate_to("Home")
    if st.button("🚀 Exam Wizard Mode"): navigate_to("Wizard")
    if st.button("💬 VeDA Neural Chat"): navigate_to("Chat")
    st.divider()
    if st.button("🧹 Clear Core Memory"):
        for k, v in default_states.items(): st.session_state[k] = v
        st.rerun()

# --- 4. COMMAND HUB (HOME SCREEN) ---
if st.session_state.app_nav == "Home":
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">VeDA AI</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem;'>The Ultimate Next-Gen Learning Ecosystem designed to rival Astra AI</p>", unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="veda-card">
            <h3>📅 Exam Prep Wizard</h3>
            <p style='color: #cbd5e1;'>Custom roadmap creation, milestone tracking, automated high-weightage topic breakdown, and active recall modules.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Exam Wizard"):
            navigate_to("Wizard")
            st.rerun()
            
    with col2:
        st.markdown("""
        <div class="veda-card">
            <h3>💬 Neural Study Chat</h3>
            <p style='color: #cbd5e1;'>Engage in deep-dive academic discourse, parse dense research PDFs, interpret diagrams, and utilize voice notes.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Neural Chat"):
            navigate_to("Chat")
            st.rerun()

# --- 5. EXAM PREP WIZARD MODE ---
elif st.session_state.app_nav == "Wizard":
    st.title("🎯 VeDA Intelligent Exam Planner")
    
    # Step 1: Subject Selection Cards
    if st.session_state.wizard_step == 1:
        st.markdown("#### Step 1: Select Your Target Discipline")
        c1, c2 = st.columns(2)
        c1.button("📐 Advanced Mathematics", on_click=set_subject, args=("Mathematics",))
        c2.button("💡 Theoretical Physics", on_click=set_subject, args=("Physics",))
        c1.button("🧪 Organic/Inorganic Chemistry", on_click=set_subject, args=("Chemistry",))
        c2.button("💻 Computer Science & Logic", on_click=set_subject, args=("Computer Science",))
        
        st.markdown("<br>", unsafe_allow_html=True)
        custom_sub = st.text_input("Or input custom competitive exam/subject:")
        if st.button("Initialize Discipline") and custom_sub:
            set_subject(custom_sub)
            st.rerun()
            
    # Step 2: Target Date
    elif st.session_state.wizard_step == 2:
        st.markdown(f"#### Step 2: Establish Timeline for {st.session_state.exam_sub}")
        st.session_state.exam_date = st.date_input("Target Examination Date", min_value=datetime.date.today())
        c1, c2 = st.columns(2)
        c1.button("⬅️ Previous", on_click=change_step, args=(1,))
        c2.button("Proceed ➡️", on_click=change_step, args=(3,))
        
    # Step 3: Target Score Slider
    elif st.session_state.wizard_step == 3:
        st.markdown("#### Step 3: Calibrate Target Score")
        st.session_state.target_score = st.slider("Expected Performance Benchmark (%)", 50, 100, 90)
        c1, c2 = st.columns(2)
        c1.button("⬅️ Previous", on_click=change_step, args=(2,))
        c2.button("Proceed ➡️", on_click=change_step, args=(4,))
        
    # Step 4: Material Upload & Strategic Compilation
    elif st.session_state.wizard_step == 4:
        st.markdown("#### Step 4: Ingest Knowledge Base")
        up_pdf = st.file_uploader("Upload Core Syllabus / Reference PDF", type="pdf")
        
        c1, c2 = st.columns(2)
        c1.button("⬅️ Previous", on_click=change_step, args=(3,))
        
        if c2.button("🚀 Compile Master Strategy"):
            if up_pdf:
                st.session_state.context_text = "".join(page.extract_text() for page in PyPDF2.PdfReader(up_pdf).pages if page.extract_text())
            
            days_remaining = (st.session_state.exam_date - datetime.date.today()).days
            with st.spinner("VeDA neural network is analyzing syllabus density and constructing your master blueprint..."):
                prompt = f"Act as a world-class academic director. Formulate an exhaustive, high-impact study strategy for {st.session_state.exam_sub} spanning {days_remaining} days targeting {st.session_state.target_score}%. Context material: {st.session_state.context_text[:5000]}. Provide clear structural headings: 'Core Focus Pillars', 'Daily Execution Rhythm', and 'Pitfalls to Avoid'."
                st.session_state.strategy_plan = model.generate_content(prompt).text
                st.session_state.wizard_step = 5
                st.rerun()

    # Step 5: Dashboard Output, Flashcards & Adaptive Quiz
    elif st.session_state.wizard_step == 5:
        st.markdown(f"### 📊 Master Blueprint: {st.session_state.exam_sub}")
        st.markdown(f'<div class="veda-card">{st.session_state.strategy_plan}</div>', unsafe_allow_html=True)
        
        col_f, col_q = st.columns(2)
        if col_f.button("🗂️ Generate Smart Flashcards"):
            with st.spinner("Synthesizing active recall flashcards..."):
                fc_prompt = f"Extract 4 high-yield conceptual Q&A pairs from: {st.session_state.context_text[:3000]}. Format strictly as Q: [Question] | A: [Answer] separated by lines."
                res = model.generate_content(fc_prompt).text
                st.session_state.flashcard_data = res.split('\n')
                st.rerun()
                
        # Render Flashcards
        if st.session_state.flashcard_data:
            st.markdown("---")
            st.markdown("#### 💡 Interactive Memory Cards")
            for card in st.session_state.flashcard_data:
                if "|" in card:
                    parts = card.split("|")
                    q = parts[0].replace("Q:", "").strip()
                    a = parts[1].replace("A:", "").strip()
                    with st.expander(f"📌 {q}"):
                        st.success(f"**Verification:** {a}")
                        
            if st.button("❓ Initialize Adaptive Evaluation Quiz"):
                with st.spinner("Generating rigorous assessment..."):
                    quiz_prompt = f"Create an elite multiple-choice question from: {st.session_state.context_text[:3000]}. Format exactly as:\nQuestion: [Text]\nA) [Opt1]\nB) [Opt2]\nC) [Opt3]\nCorrect: [A, B, or C]"
                    st.session_state.quiz_data = model.generate_content(quiz_prompt).text
                    st.rerun()

        # Render Quiz Engine
        if st.session_state.quiz_data:
            st.markdown("---")
            st.markdown("#### 🧠 Adaptive Evaluation Arena")
            lines = st.session_state.quiz_data.split('\n')
            q_text = next((l for l in lines if l.startswith("Question:")), "Question")
            correct_key = next((l for l in lines if l.startswith("Correct:")), "").replace("Correct:", "").strip()
            
            st.markdown(f"**{q_text}**")
            options = [l for l in lines if l.startswith("A)") or l.startswith("B)") or l.startswith("C)")]
            
            for opt in options:
                opt_letter = opt[0]
                if st.button(opt, key=f"quiz_opt_{opt_letter}"):
                    if opt_letter == correct_key:
                        st.success("✅ Phenomenal! Absolute precision.")
                    else:
                        st.error(f"❌ Sub-optimal. The correct validation key is {correct_key}.")
                        
        st.markdown("---")
        if st.button("🏠 Complete & Return to Hub"):
            reset_veda()
            navigate_to("Home")
            st.rerun()

# --- 6. NEURAL CHAT WITH VEDA ---
elif st.session_state.app_nav == "Chat":
    st.title("💬 VeDA Neural Workspace")
    
    # Render Chat Loop
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Professional Expander for multi-modal context input
    with st.expander("📎 Ingest Context (PDF, Image, or Audio)"):
        c1, c2 = st.columns(2)
        with c1:
            up_pdf = st.file_uploader("Document Ingestion (.PDF)", type="pdf")
            if up_pdf:
                st.session_state.context_text = "".join(page.extract_text() for page in PyPDF2.PdfReader(up_pdf).pages if page.extract_text())
                st.success("PDF knowledge indexed into VeDA core memory.")
        with c2:
            up_img = st.file_uploader("Visual Ingestion (.PNG/.JPG)", type=["png", "jpg"])
            if up_img:
                st.session_state.img_data = Image.open(up_img)
                st.success("Visual diagram buffered successfully.")
        voice_query = st.audio_input("Or transmit Voice Inquiry")

    # Native Chat Input
    prompt = st.chat_input("Consult VeDA...")
    active_query = prompt if prompt else ("Please evaluate my audio buffer submission." if voice_query else None)

    if active_query:
        st.session_state.messages.append({"role": "user", "content": active_query})
        with st.chat_message("user"):
            st.markdown(active_query)
            
        with st.chat_message("assistant"):
            with st.spinner("VeDA is processing your request..."):
                try:
                    sys_prompt = f"You are VeDA, an elite state-level AI educational architecture built to outperform all competitors. Deliver crisp, deeply intelligent answers. Context base: {st.session_state.context_text[:4000]}\nQuery: {active_query}"
                    response = model.generate_content([sys_prompt, st.session_state.img_data]) if st.session_state.img_data else model.generate_content(sys_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Neural processing exception encountered: {e}")
                    
