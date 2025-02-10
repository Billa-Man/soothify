from datetime import datetime, timedelta
import streamlit as st

# Main page configuration
st.set_page_config(
    page_title="Soothify - Your Mental Health Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.logo(
    image="media/mainlogo.png",
    size="large"
)

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    /* Main content styles */
    .main {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif;
        color: #1f1f1f;
    }
    
    /* Sidebar styles */
    .css-1d391kg {
        background-color: #ffffff;
    }
    
    .sidebar-header {
        display: flex;
        align-items: center;
        padding: 1rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid #f0f0f5;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        margin: 0.2rem 0;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.2s;
        color: #1f1f1f;
    }
    
    .nav-item:hover {
        background-color: #f8f9fa;
        color: white;
    }
    
    .nav-item.active {
        background-color: #f0f2ff;
    }
    
    .nav-icon {
        margin-right: 12px;
        width: 20px;
        opacity: 0.7;
    }
    
    /* Feature card styles */
    .feature-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0ef;
        margin: 1rem 0;
    }
    
    /* Button styles */
    .stButton > button {
        background-color: #7792E3;
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        border: none;
        font-weight: 500;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #6384dd;
        color: white;
        
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:  
    MOODS = {
    "Happy": "😊",
    "Neutral": "😐",
    "Anxious": "😰",
    "Sad": "😢",
    "Depressed": "😔"
    }  
    # Daily Mood Tracker
    st.subheader("Daily Mood Check-in")
    selected_mood = st.selectbox("How are you feeling today?", list(MOODS.keys()))
    if st.button("Log Mood"):
        st.session_state.mood_history.append({
            'timestamp': datetime.now(),
            'mood': selected_mood
        })
        st.success(f"Mood logged: {MOODS[selected_mood]} {selected_mood}")

    st.subheader("Panic Episode Tracker")
    if st.button("🚨 Record Panic Episode"):
        st.session_state.panic_episodes.append(datetime.now())
        st.warning("Panic episode recorded. Would you like to start a chat session?")

# Main content
col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.markdown("<div style='margin-top: -2rem;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Welcome to Soothify</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #7792E3;'>Your AI-Powered Mental Health Companion</h3>", unsafe_allow_html=True)
    
col_left, col_right = st.columns(2)
    
with col_left:
    st.markdown("""
    <div class="feature-card">
        <h4>Panic Attack Support:</h4>
        <ul>
            <li>Real-time panic attack assistance</li>
            <li>Breathing exercises and grounding techniques</li>
            <li>Trigger identification and management</li>
            <li>Emergency resource connections</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
with col_right:
    st.markdown("""
    <div class="feature-card">
        <h4>Mental Health Support:</h4>
        <ul>
            <li>Personalized mental health assessment</li>
            <li>Daily mood tracking and analysis</li>
            <li>Guided meditation and relaxation</li>
            <li>Progress monitoring and insights</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])

with col2:
    # Call to action
    st.markdown("""
    <div class="feature-card" style="text-align: center;">
        <h4>Ready to start your journey?</h4>
    """, unsafe_allow_html=True)
    
    if st.button("Begin Assessment", use_container_width=True):
        st.switch_page("pages/2_Assessment.py")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Info cards
    # col_left, col_right = st.columns(2)
    
    # with col_left:
    #     st.markdown("""
    #     <div class="feature-card">
    #         <h4>24/7 Support</h4>
    #         <p>Always here when you need someone to talk to</p>
    #     </div>
    #     """, unsafe_allow_html=True)
    
    # with col_right:
    #     st.markdown("""
    #     <div class="feature-card">
    #         <h4>Private & Secure</h4>
    #         <p>Your conversations are completely confidential</p>
    #     </div>
    #     """, unsafe_allow_html=True)