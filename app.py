import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import datetime

# --- 1. ASTRA APP CONFIG & CUSTOM MOBILE DOCK STYLING ---
st.set_page_config(page_title="VeDA - Astra Replica", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    .stApp { 
        background-color: #0b0f19; 
        color: #f8fafc; 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
    }
    /* Hide default sidebar and headers for clean look */
    [data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Astra Style Buttons & Cards */
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
    }
    .stButton>button:hover { 
        border-color: #f48024;
        background-color: #1e293b;
    }
    .astra-card { 
        background: #131b2e; 
        border: 1px solid #1f2937;
        padding: 20px; 
        border-radius: 20px; 
        margin-bottom: 15px; 
    }
</style>
""", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception:
    st.error("⚠️ API key missing in Streamlit Secrets.")
    st.stop()

# --- 2. SESSION STATE MEMORY ---
default_states = {
    "nav_tab": "Ask",
    "messages": [{"role": "assistant", "content": "Hello Gourav, welcome! 👋 I am VeDA, your AI academic mentor."}],
    "wizard_step": 1, 
    "exam_sub": "", 
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

def change_step(step): st.session_state.wizard_step = step
def set_subject(sub): 
    st.session_state.exam_sub = sub
    st.session_state.wizard_step = 2

# --- 3. MAIN CONTENT LOGIC BASED ON BOTTOM TABS ---
active_tab = st.session_state.nav_tab

# --- TAB 1: ASK (CHAT & MEDIA INPUT) ---
if active_tab == "Ask":
    st.markdown("### Hello Gourav, welcome! 👋")
    
    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Input simulation box matching the reference image layout
    st.markdown("---")
    user_query = st.chat_input("Ask, speak, or send a file...")
    
    # Extra utility buttons mapping to image controls (+, camera, mic, speak)
    col_bt1, col_bt2, col_bt3 = st.columns([1, 1, 2])
    with col_bt1:
        with st.popover("➕ Add"):
            up_pdf = st.file_uploader("Upload PDF File", type="pdf")
            if up_pdf:
                try:
                    reader = PyPDF2.PdfReader(up_pdf)
                    raw_text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
                    st.session_state.context_text = raw_text[:3000]
                    st.success("File indexed successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
    with col_bt2:
        up_img = st.file_uploader("📷 Camera/Photo", type=["png", "jpg"], label_visibility="collapsed")
        if up_img:
            st.session_state.img_data = Image.open(up_img)
            st.success("Photo attached!")
    with col_bt3:
        voice_note = st.audio_input("🎙️ Speak", label_visibility="collapsed")

    final_input = user_query if user_query else ("Please process my attached audio note." if voice_note else None)

    if final_input:
        st.session_state.messages.append({"role": "user", "content": final_input})
        with st.chat_message("user"):
            st.markdown(final_input)
            
        with st.chat_message("assistant"):
            with st.spinner("VeDA is thinking..."):
                try:
                    sys_prompt = f"You are VeDA, an elite AI tutor. Context: {st.session_state.context_text[:3000]}\nQuery: {final_input}"
                    response = model.generate_content([sys_prompt, st.session_state.img_data]) if st.session_state.img_data else model.generate_content(sys_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")

# --- TAB 2: EXAMS (WIZARD FLOW) ---
elif active_tab == "Exams":
    
    # Step 1: Subject Selection Grid
    if st.session_state.wizard_step == 1:
        st.markdown("### Prepare for your Exams with AI")
        if st.button("➕ Create new exam", type="primary"):
            st.session_state.wizard_step = 1.1
            st.rerun()
            
        if st.session_state.wizard_step == 1.1:
            st.markdown("### Choose a subject")
            custom_sub = st.text_input("Type your subject...")
            if st.button("Add custom subject") and custom_sub:
                set_subject(custom_sub)
                st.rerun()
                
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📐 Math"): set_subject("Math")
                if st.button("🧪 Chemistry"): set_subject("Chemistry")
                if st.button("📚 English"): set_subject("English")
            with col2:
                if st.button("💡 Physics"): set_subject("Physics")
                if st.button("💻 Computer Science"): set_subject("Computer Science")
                if st.button("🧬 Biology"): set_subject("Biology")

    # Step 2: Exam Timeline Date Picker
    elif st.session_state.wizard_step == 2:
        st.markdown(f"### When is your {st.session_state.exam_sub} exam?")
        if st.button("🚨 Tomorrow"):
            st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=1)
            change_step(3)
            st.rerun()
        if st.button("⚡ In 2 days"):
            st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=2)
            change_step(3)
            st.rerun()
        if st.button("⚡ In 3 days"):
            st.session_state.exam_date = datetime.date.today() + datetime.timedelta(days=3)
            change_step(3)
            st.rerun()
            
        st.session_state.exam_date = st.date_input("Pick a date", min_value=datetime.date.today())
        if st.button("Continue", type="primary"): change_step(3)

    # Step 3: Target Score / Mastery Goal Slider
    elif st.session_state.wizard_step == 3:
        st.markdown("### What is your target score?")
        st.session_state.target_score = st.slider("Mastery goal (%)", 50, 100, 85)
        if st.button("Continue", type="primary"): change_step(4)

    # Step 4: School Details
    elif st.session_state.wizard_step == 4:
        st.markdown("### Confirm your school details")
        st.text_input("Search school")
        st.session_state.edu_level = st.selectbox("Education level", [
            "Secondary stage (grades 9-12)",
            "University / higher education"
        ])
        st.session_state.grade = st.selectbox("Grade", ["9. grade", "10. grade", "11. grade", "12. grade"])
        
        if st.button("Continue to Upload Notes", type="primary"): change_step(5)

    # Step 5: Upload Notes & Strategy Generation
    elif st.session_state.wizard_step == 5:
        st.markdown("### Upload your study notes")
        up_pdf = st.file_uploader("Upload PDF material", type="pdf")
        
        if st.button("🚀 Generate Strategy Blueprint", type="primary"):
            if up_pdf:
                try:
                    reader = PyPDF2.PdfReader(up_pdf)
                    raw_text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
                    st.session_state.context_text = raw_text[:3000]
                except Exception as e:
                    st.error(f"Error: {e}")
            
            with st.spinner("Building your blueprint..."):
                prompt = f"Create a study strategy for {st.session_state.exam_sub} targeting {st.session_state.target_score}%. Context: {st.session_state.context_text}"
                st.session_state.strategy_plan = model.generate_content(prompt).text
                st.session_state.wizard_step = 6
                st.rerun()

    # Step 6: Strategy Dashboard & Flashcards/Quiz
    elif st.session_state.wizard_step == 6:
        st.markdown(f"### 📊 Blueprint: {st.session_state.exam_sub}")
        st.markdown(f'<div class="astra-card">{st.session_state.strategy_plan}</div>', unsafe_allow_html=True)
        
        if st.button("🗂️ Learn with Flashcards"):
            res = model.generate_content(f"Create 3 Q&A flashcards from: {st.session_state.context_text}. Format as Q: [Q] | A: [A]").text
            st.session_state.flashcard_data = res.split('\n')
            st.rerun()
            
        if st.session_state.flashcard_data:
            for card in st.session_state.flashcard_data:
                if "|" in card:
                    parts = card.split("|")
                    with st.expander(parts[0].replace("Q:", "📌")):
                        st.success(parts[1].replace("A:", ""))
                        
            if st.button("❓ Ready for Quiz", type="primary"):
                st.session_state.quiz_data = model.generate_content(f"Create 1 MCQ from: {st.session_state.context_text}. Format: Question: [Text]\nA) [Opt]\nB) [Opt]\nC) [Opt]\nCorrect: [A/B/C]").text
                st.rerun()

        if st.session_state.quiz_data:
            lines = st.session_state.quiz_data.split('\n')
            st.write(lines[0])
            for line in lines[1:4]:
                if st.button(line):
                    if line.startswith(lines[-1].replace("Correct:", "").strip()):
                        st.success("✅ Correct!")
                    else:
                        st.error("❌ Incorrect!")

# --- TAB 3: APPS (EXTRAS & TOOLS) ---
elif active_tab == "Apps":
    st.markdown("### 🧩 VeDA Ecosystem Apps")
    st.markdown("""
    <div class="astra-card">
        <h4>⚡ Formula Vault</h4>
        <p style="color: #94a3b8;">Quick access to mathematical and physical equations.</p>
    </div>
    <div class="astra-card">
        <h4>⏱️ Pomodoro Focus Timer</h4>
        <p style="color: #94a3b8;">Maintain deep work intervals for peak retention.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. BOTTOM DOCK NAVIGATION BAR (MATCHING REFERENCE IMAGE) ---
st.markdown("<br><br>", unsafe_allow_html=True)
col_d1, col_d2, col_d3, col_d4 = st.columns(4)

with col_d1:
    if st.button("💬 Ask"):
        st.session_state.nav_tab = "Ask"
        st.rerun()
with col_d2:
    if st.button("🎯 Exams"):
        st.session_state.nav_tab = "Exams"
        st.rerun()
with col_d3:
    if st.button("📦 Apps"):
        st.session_state.nav_tab = "Apps"
        st.rerun()
with col_d4:
    if st.button("⚙️ More"):
        st.markdown("VeDA AI v3.6 Pro Edition")
        
