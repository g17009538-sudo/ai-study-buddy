import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image

# 1. App UI & Custom Design (Peach & Orange Theme)
st.set_page_config(page_title="AI Study Tutor", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    /* Main Background - Soft Peach */
    .stApp {
        background-color: #FEF5F0;
    }
    
    /* Sidebar Design */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 2px solid #F48024;
    }
    
    /* Buttons Customization */
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #F48024;
        color: #F48024;
    }
    .stButton>button:hover {
        background-color: #F48024;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 2. API Setup
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Using the exact model version requested by Google API
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception as e:
    st.error("⚠️ API key is not set in the background. Please check Streamlit Secrets.")
    st.stop()

# 3. Chat Memory Setup (To remember chat history)
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
    
    # Sidebar buttons to trigger chat actions
    btn_explain = st.button("🖼️ Explain Diagram")
    btn_quiz = st.button("❓ Generate Quiz")
    btn_flash = st.button("🗂️ Generate Flashcards")
    btn_clear = st.button("🗑️ Clear Chat History")

# Clear chat history logic
if btn_clear:
    st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared! Ask a new question."}]
    st.rerun()

# 5. Main Chat Interface
st.title("🎓 Smart AI Study Tutor")

# Display previous chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. User Input or Sidebar Button Actions
prompt = st.chat_input("Type your message here...")
action_prompt = None

if prompt:
    action_prompt = prompt
elif btn_explain:
    action_prompt = "Explain my uploaded diagram in simple educational terms."
elif btn_quiz:
    action_prompt = "Generate a 5-question multiple-choice quiz with answers based on my uploaded PDF notes."
elif btn_flash:
    action_prompt = "Create 5 important Q&A flashcards based on my uploaded PDF notes."

if action_prompt:
    # Display user message and save to memory
    st.session_state.messages.append({"role": "user", "content": action_prompt})
    with st.chat_message("user"):
        st.markdown(action_prompt)
        
    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Provide context (PDF) and chat history to AI
                context = f"Context from PDF:\n{st.session_state.pdf_text[:5000]}\n\n" if st.session_state.pdf_text else ""
                history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-4:-1]]) # Last 3 messages
                
                full_prompt = f"You are a helpful, professional AI study tutor. Answer clearly and accurately in English.\n\n{context}\n\nRecent Chat History:\n{history_text}\n\nUser New Request: {action_prompt}"
                
                if st.session_state.img_data and (btn_explain or action_prompt == prompt):
                    response = model.generate_content([full_prompt, st.session_state.img_data])
                else:
                    response = model.generate_content(full_prompt)
                
                st.markdown(response.text)
                
                # Save AI response to memory
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"⚠️ Connection issue occurred. Please try again.")
                
