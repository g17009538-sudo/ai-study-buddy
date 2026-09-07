import streamlit as st
import google.generativeai as genai
import PyPDF2
import datetime

# --- 1. ASTRA NATIVE FULL-HTML/CSS MOBILE ENGINE CONFIG ---
st.set_page_config(page_title="VeDA - Astra Replica", page_icon="🎓", layout="centered")

# Hide Streamlit Default Headers & Footers
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .stApp { background-color: #0b0f19; color: #f8fafc; }
</style>
""", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception:
    st.error("⚠️ API key missing in Streamlit Secrets.")
    st.stop()

# --- 2. SESSION STATE MEMORY ---
if "active_tab" not in st.session_state: st.session_state.active_tab = "Ask"
if "wizard_step" not in st.session_state: st.session_state.wizard_step = 1
if "exam_sub" not in st.session_state: st.session_state.exam_sub = "Math"
if "messages" not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Hello Gourav, welcome! 👋 I am VeDA, your dedicated AI academic mentor."}]
if "context_text" not in st.session_state: st.session_state.context_text = ""
if "strategy_plan" not in st.session_state: st.session_state.strategy_plan = ""

# --- 3. EMBEDDED ASTRA UI (HTML/CSS/JS INJECTED) ---
astra_html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VeDA Astra Edition</title>
    <style>
        body {{
            background-color: #0b0f19;
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 16px;
            padding-bottom: 90px;
        }}
        .welcome-box {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 15px;
        }}
        .ai-card {{
            background: #131b2e;
            border: 1px solid #1f2937;
            border-radius: 18px;
            padding: 18px;
            margin-bottom: 15px;
        }}
        .subject-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }}
        .sub-btn {{
            background: #131b2e;
            border: 1px solid #1f2937;
            color: white;
            padding: 14px;
            border-radius: 14px;
            text-align: left;
            font-size: 0.95rem;
            cursor: pointer;
            transition: 0.2s;
        }}
        .sub-btn:hover {{
            border-color: #f48024;
            background: #1e293b;
        }}
        /* Bottom Dock */
        .bottom-dock {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: #07090e;
            border-top: 1px solid #1f2937;
            display: flex;
            justify-content: space-around;
            padding: 12px 0;
            z-index: 1000;
        }}
        .dock-item {{
            color: #94a3b8;
            text-align: center;
            font-size: 0.85rem;
            cursor: pointer;
            text-decoration: none;
        }}
        .dock-item.active {{
            color: #f48024;
            font-weight: bold;
        }}
    </style>
</head>
<body>

    <div class="welcome-box">Hello Gourav, welcome! 👋</div>

    <div class="ai-card">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <span style="background: #f48024; padding: 6px 10px; border-radius: 10px;">🤖</span>
            <span>I am <b>VeDA</b>, your dedicated AI academic mentor.</span>
        </div>
    </div>

    <div style="margin-top: 20px;">
        <h3>Choose a subject</h3>
        <p style="color: #94a3b8; font-size: 0.85rem;">Select your exam discipline below:</p>
        
        <div class="subject-grid">
            <button class="sub-btn" onclick="window.location.href='/?sub=Math'">📐 Math</button>
            <button class="sub-btn" onclick="window.location.href='/?sub=Physics'">💡 Physics</button>
            <button class="sub-btn" onclick="window.location.href='/?sub=Chemistry'">🧪 Chemistry</button>
            <button class="sub-btn" onclick="window.location.href='/?sub=ComputerScience'">💻 Computer Science</button>
            <button class="sub-btn" onclick="window.location.href='/?sub=English'">📚 English</button>
            <button class="sub-btn" onclick="window.location.href='/?sub=Biology'">🧬 Biology</button>
        </div>
    </div>

</body>
</html>
"""

# Render Native HTML Layout for Astra Replica
st.components.v1.html(astra_html_template, height=650, scrolling=True)

# --- 4. BOTTOM DOCK SIMULATION IN STREAMLIT ---
st.markdown("""
<style>
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #07090e;
        padding: 10px;
        display: flex;
        justify-content: space-around;
        border-top: 1px solid #1f2937;
        z-index: 99999;
    }
</style>
""", unsafe_allow_html=True)

col_d1, col_d2, col_d3 = st.columns(3)
with col_d1:
    if st.button("💬 Ask Workspace"): st.session_state.active_tab = "Ask"
with col_d2:
    if st.button("🎯 Exam Planner"): st.session_state.active_tab = "Exams"
with col_d3:
    if st.button("📦 Ecosystem Apps"): st.session_state.active_tab = "Apps"
