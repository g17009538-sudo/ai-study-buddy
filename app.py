import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import datetime

# 1. UI & Custom Theme
st.set_page_config(page_title="AI Study Tutor", page_icon="🎓", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #FEF5F0; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 2px solid #F48024; }
    .stButton>button { border-radius: 8px; border: 1px solid #F48024; color: #F48024; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #F48024; color: white; }
    .strategy-box { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #F48024; margin-bottom: 15px; }
    
    /* Custom Chat Bar Styling */
    .custom-chat-row { display: flex; align-items: center; gap: 10px; background: white; padding: 10px; border-radius: 30px; box-shadow: 0px 2px 10px rgba(0,0,0,0.1); margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception:
    st.error("⚠️ API key missing.")
    st.stop()

# 2. Session States
default_states = {
    "messages": [{"role": "assistant", "content": "Welcome! How can I assist your studies today?"}],
    "wizard_step": 1, "exam_sub": "", "exam_date": datetime.date.today(), "target_score": 80,
    "strategy_plan": "", "context_text": "", "img_data": None,
    "flashcard_data": [], "quiz_data": None, "quiz_answered": False
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

def change_step(step): st.session_state.wizard_step = step
def set_subject(sub): st.session_state.exam_sub = sub; st.session_state.wizard_step = 2
def reset_wizard():
    st.session_state.wizard_step = 1
    st.session_state.flashcard_data = []
    st.session_state.quiz_data = None

# Sidebar
with st.sidebar:
    app_mode = st.radio("Navigation", ["💬 Chat & Tools", "📅 Exam Prep Mode"])
    if st.button("🗑️ Clear Memory"): st.session_state.messages = default_states["messages"]; st.rerun()

# ----------------- MODE 1: EXAM PREP WIZARD -----------------
if app_mode == "📅 Exam Prep Mode":
    st.title("Interactive Exam Planner")
    
    # Step 1: Subject
    if st.session_state.wizard_step == 1:
        st.subheader("Step 1: Choose a subject")
        c1, c2 = st.columns(2)
        c1.button("📐 Mathematics", on_click=set_subject, args=("Mathematics",))
        c2.button("💡 Physics", on_click=set_subject, args=("Physics",))
        custom_sub = st.text_input("Or type your subject:")
        if st.button("Continue") and custom_sub: set_subject(custom_sub)
    
    # Step 2: Date
    elif st.session_state.wizard_step == 2:
        st.subheader(f"Step 2: When is your {st.session_state.exam_sub} exam?")
        st.session_state.exam_date = st.date_input("Select Date", min_value=datetime.date.today())
        c1, c2 = st.columns(2)
        c1.button("Back", on_click=change_step, args=(1,))
        c2.button("Next", on_click=change_step, args=(3,))
        
    # Step 3: Target Score
    elif st.session_state.wizard_step == 3:
        st.subheader("Step 3: What is your target score?")
        st.session_state.target_score = st.slider("Expected Marks (%)", 0, 100, 80)
        c1, c2 = st.columns(2)
        c1.button("Back", on_click=change_step, args=(2,))
        c2.button("Next", on_click=change_step, args=(4,))
        
    # Step 4: Upload & AI Strategy Generation
    elif st.session_state.wizard_step == 4:
        st.subheader("Step 4: Add your study material")
        up_pdf = st.file_uploader("Upload Notes (PDF)", type="pdf")
        c1, c2 = st.columns(2)
        c1.button("Back", on_click=change_step, args=(3,))
        
        if c2.button("🚀 Generate AI Strategy"):
            if up_pdf:
                st.session_state.context_text = "".join(page.extract_text() for page in PyPDF2.PdfReader(up_pdf).pages if page.extract_text())
            with st.spinner("Analyzing syllabus..."):
                prompt = f"Create a short study strategy for {st.session_state.exam_sub}. Include important topics and how to study them based on this text: {st.session_state.context_text[:3000]}"
                st.session_state.strategy_plan = model.generate_content(prompt).text
                st.session_state.wizard_step = 5
                st.rerun()

    # Step 5: Master Strategy -> True AI Flashcards -> True AI Quiz
    elif st.session_state.wizard_step == 5:
        st.subheader("📊 Your Master Strategy")
        st.markdown(f'<div class="strategy-box">{st.session_state.strategy_plan}</div>', unsafe_allow_html=True)
        
        # Flashcards Generation
        if st.button("🗂️ Learn with Flashcards"):
            with st.spinner("Generating Flashcards from your notes..."):
                prompt = f"Create 3 simple Q&A flashcards from this text: {st.session_state.context_text[:3000]}. Format strictly as:\nQ: [Question]\nA: [Answer]|Q: [Question]\nA: [Answer]"
                res = model.generate_content(prompt).text
                st.session_state.flashcard_data = res.split("|")
                st.rerun()

        # Display Flashcards
        if st.session_state.flashcard_data:
            st.divider()
            st.subheader("Flip Cards")
            for card in st.session_state.flashcard_data:
                if "Q:" in card and "A:" in card:
                    q = card.split("A:")[0].replace("Q:", "").strip()
                    a = card.split("A:")[1].strip()
                    with st.expander(f"🤔 {q}"):
                        st.success(f"💡 {a}")
            
            # Quiz Generation (Only appears after Flashcards)
            if st.button("❓ Ready for Quiz"):
                with st.spinner("Preparing a specific question..."):
                    prompt = f"Create 1 multiple choice question based on this text: {st.session_state.context_text[:3000]}. Format exactly like this:\nQuestion: [Q]\nOption A: [Opt]\nOption B: [Opt]\nOption C: [Opt]\nCorrect: [A, B, or C]"
                    quiz_text = model.generate_content(prompt).text
                    st.session_state.quiz_data = quiz_text
                    st.session_state.quiz_answered = False
                    st.rerun()

        # Display Quiz
        if st.session_state.quiz_data:
            st.divider()
            st.subheader("Knowledge Check")
            lines = st.session_state.quiz_data.split('\n')
            question = next((l for l in lines if l.startswith("Question:")), "Question not found")
            correct_ans = next((l for l in lines if l.startswith("Correct:")), "").replace("Correct:", "").strip()
            
            st.write(f"**{question.replace('Question:', '').strip()}**")
            
            opts = [l for l in lines if l.startswith("Option")]
            c1, c2, c3 = st.columns(3)
            cols = [c1, c2, c3]
            
            for i, opt in enumerate(opts[:3]):
                opt_letter = opt.split(":")[0].replace("Option", "").strip()
                if cols[i].button(opt):
                    if opt_letter == correct_ans:
                        st.success("✅ Correct! Excellent retention.")
                    else:
                        st.error(f"❌ Incorrect. The right answer was {correct_ans}.")
                        
            if st.button("🏠 Return to Start"): reset_wizard(); st.rerun()

# ----------------- MODE 2: CHAT & TOOLS (Custom UI Row) -----------------
elif app_mode == "💬 Chat & Tools":
    st.title("🎓 Smart AI Study Tutor")
    
    # Chat History
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    st.write("")
    st.write("")
    
    # Custom Integrated Input Row (Replacing st.chat_input)
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        with st.popover("➕"):
            up_pdf = st.file_uploader("Upload PDF", type="pdf")
            if up_pdf: st.session_state.context_text = "".join(page.extract_text() for page in PyPDF2.PdfReader(up_pdf).pages if page.extract_text()); st.success("Loaded!")
    with col2:
        user_query = st.text_input("Ask Gemini...", label_visibility="collapsed")
    with col3:
        voice_input = st.audio_input("Mic", label_visibility="collapsed")

    final_query = user_query if user_query else ("Please answer my voice note" if voice_input else None)

    if final_query:
        st.session_state.messages.append({"role": "user", "content": final_query})
        st.rerun() # Forces the chat to update, the processing will happen on next render

    # AI Processing Logic (Triggers after rerun if last message is user)
    if st.session_state.messages[-1]["role"] == "user":
        with st.spinner("Analyzing..."):
            sys_prompt = f"Answer clearly. Context: {st.session_state.context_text[:4000]}\nQuery: {st.session_state.messages[-1]['content']}"
            response = model.generate_content(sys_prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
