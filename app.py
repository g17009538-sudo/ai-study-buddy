import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image

# App UI aur Sidebar Setup
st.set_page_config(page_title="AI Study Tutor", page_icon="🎓", layout="wide")
st.title("🎓 Smart AI Study Tutor")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Smart Auto-Model Detector: Khud check karega konsa AI chalega
    valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    if not valid_models:
        st.error("⚠️ Tumhari API Key se koi AI model nahi mil raha. Kripya aistudio.google.com se nayi key banayein.")
        st.stop()
        
    # Best model select karna
    best_model = valid_models[0]
    for m_name in valid_models:
        if '1.5-flash' in m_name:
            best_model = m_name
            break
            
    model = genai.GenerativeModel(best_model)

except KeyError:
    st.error("⚠️ Background mein API key set nahi hai. Kripya Streamlit Secrets check karein.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}. Agar yeh baar-baar aaye toh Google AI Studio se ek nayi API key bana kar Streamlit Secrets mein update karein.")
    st.stop()

# Sidebar: Tools aur Uploads
with st.sidebar:
    st.header("📂 Study Material")
    uploaded_pdf = st.file_uploader("📝 Upload Notes (PDF)", type="pdf")
    uploaded_img = st.file_uploader("🖼️ Upload Diagram (Image)", type=["png", "jpg", "jpeg"])
    
    st.divider()
    st.header("⚙️ Kya karna hai?")
    action = st.radio("Apna tool select karo:", ["💬 General Chat", "🖼️ Diagram Explain", "❓ Quiz Banao", "🗂️ Flashcards Banao"])

# Text aur Image process karna
pdf_text = ""
if uploaded_pdf:
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
        pdf_text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        st.sidebar.success("✅ PDF Load ho gayi!")
    except Exception:
        st.sidebar.error("⚠️ PDF read nahi ho paayi.")

img_data = None
if uploaded_img:
    img_data = Image.open(uploaded_img)
    st.sidebar.success("✅ Image Load ho gayi!")
    st.sidebar.image(img_data, use_container_width=True)

# Main Screen Logic
if action == "💬 General Chat":
    st.subheader("Mujhse padhai ka koi bhi sawal poocho!")
    user_question = st.text_input("Sawal type karo...")
    if st.button("Poocho"):
        if user_question:
            with st.spinner("Soch raha hoon..."):
                try:
                    context = f"Context from PDF:\n{pdf_text[:5000]}\n\n" if pdf_text else ""
                    prompt = f"{context}User Question: {user_question}"
                    if img_data:
                        response = model.generate_content([prompt, img_data])
                    else:
                        response = model.generate_content(prompt)
                    st.write(response.text)
                except Exception as e:
                    st.error(f"⚠️ Jawab dene mein problem aayi: {e}")
        else:
            st.warning("Pehle koi sawal likho!")

elif action == "🖼️ Diagram Explain":
    st.subheader("Diagram Explanation Tool")
    if img_data:
        if st.button("Samjhao"):
            with st.spinner("Diagram padh raha hoon..."):
                try:
                    response = model.generate_content(["Explain this diagram in simple educational terms.", img_data])
                    st.write(response.text)
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
    else:
        st.info("👈 Pehle sidebar se koi diagram (image) upload karo.")

elif action == "❓ Quiz Banao":
    st.subheader("Practice Quiz Generator")
    if pdf_text:
        if st.button("Quiz Generate Karo"):
            with st.spinner("Questions ban rahe hain..."):
                try:
                    response = model.generate_content(f"Create a 5-question multiple choice quiz with answers from this text:\n\n{pdf_text[:10000]}")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
    else:
        st.info("👈 Pehle sidebar se notes (PDF) upload karo.")

elif action == "🗂️ Flashcards Banao":
    st.subheader("Smart Flashcards")
    if pdf_text:
        if st.button("Flashcards Generate Karo"):
            with st.spinner("Flashcards ban rahe hain..."):
                try:
                    response = model.generate_content(f"Create 5 important flashcards with Question and Answer format from this text:\n\n{pdf_text[:10000]}")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
    else:
        st.info("👈 Pehle sidebar se notes (PDF) upload karo.")
        
