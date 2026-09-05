import streamlit as st
import google.generativeai as genai
import PyPDF2

st.set_page_config(page_title="AI Study Buddy", page_icon="📚")
st.title("📚 AI Study Buddy")
st.write("Apne study notes upload karo aur AI se Summary, Flashcards aur Quizzes banwao!")

api_key = st.text_input("Apni Google Gemini API Key yahan paste karo:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    # Using the most stable model name
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    uploaded_file = st.file_uploader("Apne PDF notes upload karo", type="pdf")

    if uploaded_file is not None:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
            st.success("File upload ho gayi!")

            tab1, tab2, tab3 = st.tabs(["📝 Summary", "🗂️ Flashcards", "❓ Quiz"])

            with tab1:
                if st.button("Summary Banao"):
                    with st.spinner("AI padh raha hai..."):
                        response = model.generate_content(f"Summarize these notes in detail:\n\n{text[:10000]}")
                        st.write(response.text)

            with tab2:
                if st.button("Flashcards Banao"):
                    with st.spinner("Flashcards ban rahe hain..."):
                        response = model.generate_content(f"Create 5 important flashcards with Question and Answer format from these notes:\n\n{text[:10000]}")
                        st.write(response.text)

            with tab3:
                if st.button("Practice Quiz Banao"):
                    with st.spinner("Quiz generate ho raha hai..."):
                        response = model.generate_content(f"Create a 5-question multiple choice quiz with answers at the end based on these notes:\n\n{text[:10000]}")
                        st.write(response.text)
        except Exception as e:
            st.error(f"Ek error aaya hai: {e}")
else:
    st.warning("Start karne ke liye upar apni API key daalo.")
