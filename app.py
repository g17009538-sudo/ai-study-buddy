import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import datetime

# 1. App UI & Custom Design
st.set_page_config(page_title="AI Study Tutor", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FEF5F0; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 2px solid #F48024; }
    .stButton>button { border-radius: 20px; border: 1px solid #F48024; color: #F48024; }
    .stButton>button:hover { background-color: #F48024; color: white; }
</style>
""", unsafe_allow_html=True)

# 2. API Setup
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception as e:
    st.error("⚠️ API key is not set in the background. Please check Streamlit Secrets.")
    st.stop()

# 3. Chat Memory Setup
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I am your AI Study Tutor. Upload your notes or ask me a question directly! 😊"}]
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "img_data" not in st.session_state:
    st.session_state.img_data = None

# 4. Sidebar - Tools & Uploads
with st.sidebar:
    st.header("📂 Upload Material")
    
    uploaded_pdf = st.file_uploader("📝 Upload Notes (PDF)", type="pdf")
    if uploaded_pdf:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            st.session_state.pdf_text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
            st.success("✅ PDF loaded successfully!")
        except:
            st.error("⚠️ Could not read the PDF file.")

    uploaded_img = st.file_uploader("🖼️ Upload Diagram (Image)", type=["png", "jpg", "jpeg"])
    if uploaded_img:
        st.session_state.img_data = Image.open(uploaded_img)
        st.success("✅ Diagram loaded successfully!")
        st.image(st.session_state.img_data, use_container_width=True)
        
    st.divider()
    st.header("⚙️ Smart Actions")
    
    # Updated Menu Options
    action = st.radio("Choose Mode:", ["💬 General Chat", "📅 Exam Prep Mode", "🖼️ Explain Diagram", "❓ Generate Quiz", "🗂️ Generate Flashcards"])
    
    st.divider()
    btn_clear = st.button("🗑️ Clear Chat History")

if btn_clear:
    st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared! Ask a new question."}]
    st.rerun()

# 5. Main Screen Setup
st.title("🎓 Smart AI Study Tutor")

action_prompt = None

# Exam Prep Mode UI
if action == "📅 Exam Prep Mode":
    st.subheader("📅 Exam Preparation Plan")
    st.write("Fill in your exam details below to generate a tailored study plan from your notes.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        exam_subject = st.text_input("Subject", placeholder="e.g., JEE Main Physics")
    with col2:
        exam_date = st.date_input("Exam Date", min_value=datetime.date.today())
    with col3:
        target_score = st.text_input("Target Score", placeholder="e.g., 90% or 250+")
        
    if st.button("🚀 Create My Study Plan"):
        if not st.session_state.pdf_text:
            st.warning("Please upload your PDF notes in the sidebar first!")
        elif not exam_subject:
            st.warning("Please enter the subject name.")
        else:
            days_left = (exam_date - datetime.date.today()).days
            action_prompt = f"I am preparing for the {exam_subject} exam in {days_left} days. My target score is {target_score}. Based on the uploaded notes, create a highly structured, day-by-day study plan. Include topic breakdowns, a strategy for flashcard revision, and a practice test schedule."

# Display Chat History (for all modes)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input Logic
prompt = st.chat_input("Type your message here..." if action == "💬 General Chat" else "Chat disabled in this tool. Use buttons above.")

# Handle Sidebar Tools
if action == "💬 General Chat" and prompt:
    action_prompt = prompt
elif action == "🖼️ Explain Diagram" and st.button("Explain Uploaded Diagram"):
    action_prompt = "Explain my uploaded diagram in simple educational terms."
elif action == "❓ Generate Quiz" and st.button("Create Practice Quiz"):
    action_prompt = "Generate a 5-question multiple-choice quiz with answers based on my uploaded PDF notes."
elif action == "🗂️ Generate Flashcards" and st.button("Create Flashcards"):
    action_prompt = "Create 5 important Q&A flashcards based on my uploaded PDF notes."

# Generate AI Response
if action_prompt:
    st.session_state.messages.append({"role": "user", "content": action_prompt})
    with st.chat_message("user"):
        st.markdown(action_prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                context = f"Context from PDF:\n{st.session_state.pdf_text[:5000]}\n\n" if st.session_state.pdf_text else ""
                history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-4:-1]])
                
                full_prompt = f"You are a helpful, professional AI study tutor. Answer clearly and accurately in English.\n\n{context}\n\nRecent Chat History:\n{history_text}\n\nUser New Request: {action_prompt}"
                
                if st.session_state.img_data and ("diagram" in action_prompt.lower() or action == "💬 General Chat"):
                    response = model.generate_content([full_prompt, st.session_state.img_data])
                else:
                    response = model.generate_content(full_prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"⚠️ Connection issue occurred. Please try again.")
                
