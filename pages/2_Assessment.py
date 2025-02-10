import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Soothify - Assessment",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.logo(
    image="media/mainlogo.png",
    size="large"
)

# Initialize session state for previous assessment
if 'last_assessment' not in st.session_state:
    st.session_state.last_assessment = None

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Proxima+Nova:wght@400;600&display=swap');
    
    .main {
        background-color: #f0f0f5;
    }
    
    h1, h2, h3 {
        font-family: 'Proxima Nova', sans-serif;
        color: #262730;
    }
    
    p, div {
        font-family: 'Source Sans Pro', sans-serif;
        color: #262730;
    }

    .question-container {
        background-color: #F0F2F5;
        padding: 30px;
        border-radius: 10px;
        margin: 20px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stProgress > div > div > div {
        background-color: #A8B9ED;
    }
    
    .stButton > button {
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 18px;
        height: 3em;
        background-color: #7792E3 !important;
        color: white;
        border: none;
        border-radius: 5px;
        transition: transform 0.2s;
    }

    .previous-button > button {
        background-color: #6c757d !important;
        color:white;
    }

    .score-card {
        background-color: #e0e0ef;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }

    .severity-mild { color: #4CAF50; }
    .severity-moderate { color: #FFA726; }
    .severity-severe { color: #EF5350; }
    </style>
""", unsafe_allow_html=True)

# Questions dictionary with scoring weights
questions = {
    'q1': {
        'text': "Over the past 2 weeks, how often have you felt down, depressed, or hopeless?",
        'options': ["Not at all", "Several days", "More than half the days", "Nearly every day"],
        'weights': [0, 1, 2, 3]
    },
    'q2': {
        'text': "How often do you feel overwhelmed by your daily responsibilities?",
        'options': ["Never", "Sometimes", "Often", "Always"],
        'weights': [0, 1, 2, 3]
    },
    'q3': {
        'text': "How would you rate your sleep quality over the past week?",
        'options': ["Excellent", "Good", "Fair", "Poor"],
        'weights': [0, 1, 2, 3]
    },
    'q4': {
        'text': "How often do you feel anxious or worried about various aspects of your life?",
        'options': ["Rarely", "Occasionally", "Frequently", "Constantly"],
        'weights': [0, 1, 2, 3]
    },
    'q5': {
        'text': "How would you describe your energy levels throughout the day?",
        'options': ["Very energetic", "Moderately energetic", "Low energy", "Extremely fatigued"],
        'weights': [0, 1, 2, 3]
    },
    'q6': {
        'text': "How often do you have trouble concentrating on tasks?",
        'options': ["Rarely", "Sometimes", "Often", "Almost always"],
        'weights': [0, 1, 2, 3]
    },
    'q7': {
        'text': "How would you rate your stress levels in the past month?",
        'options': ["Low", "Moderate", "High", "Very high"],
        'weights': [0, 1, 2, 3]
    },
    'q8': {
        'text': "How often do you feel isolated or lonely?",
        'options': ["Never", "Occasionally", "Frequently", "Almost always"],
        'weights': [0, 1, 2, 3]
    },
    'q9': {
        'text': "How would you rate your ability to cope with challenges?",
        'options': ["Very good", "Good", "Fair", "Poor"],
        'weights': [0, 1, 2, 3]
    },
    'q10': {
        'text': "How often do you experience physical symptoms of stress (headaches, tension, etc.)?",
        'options': ["Rarely", "Sometimes", "Often", "Very often"],
        'weights': [0, 1, 2, 3]
    }
}

# Initialize session state
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'score' not in st.session_state:
    st.session_state.score = 0

# Main content
st.markdown("<h1 style='text-align: center; color: #262730;'>Mental Health Assessment</h1>", unsafe_allow_html=True)

# Only show progress during questions
if st.session_state.current_question < len(questions):
    progress = st.session_state.current_question / len(questions)
    st.progress(progress)
    st.markdown(f"Question {st.session_state.current_question + 1} of {len(questions)}")
    
    q_id = f'q{st.session_state.current_question + 1}'
    question = questions[q_id]
    
    st.markdown(f"""
        <div class="question-container">
            <p>{question['text']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    default_index = (question['options'].index(st.session_state.responses[q_id]) 
                    if q_id in st.session_state.responses 
                    else 0)
    
    response = st.radio("", question['options'], 
                       key=q_id, 
                       label_visibility="collapsed",
                       index=default_index)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        left_col, right_col = st.columns(2)
        
        with left_col:
            if st.session_state.current_question > 0:
                if st.button("← Previous", use_container_width=True, key="prev"):
                    st.session_state.responses[q_id] = response
                    score_index = question['options'].index(response)
                    st.session_state.score -= question['weights'][score_index]
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with right_col:
            next_button_text = "Next →" if st.session_state.current_question < len(questions)-1 else "Submit"
            if st.button(next_button_text, use_container_width=True, key="next"):
                st.session_state.responses[q_id] = response
                score_index = question['options'].index(response)
                st.session_state.score += question['weights'][score_index]
                st.session_state.current_question += 1
                st.rerun()

# Show results when complete
if st.session_state.current_question == len(questions):
    max_score = sum(max(q['weights']) for q in questions.values())
    score_percentage = (st.session_state.score / max_score) * 100
    
    if score_percentage < 30:
        severity = "mild"
        color = "severity-mild"
        recommendation = "Based on your responses, we recommend exploring AI chat, reading wellness blogs, and trying some guided exercises."
        buttons = [("AI Chat", "pages/3_Chat.py"), ("Wellness Blogs", "pages/7_Blogs.py"), ("Guided Exercises", "pages/6_Exercises.py")]
    elif score_percentage < 60:
        severity = "moderate"
        color = "severity-moderate"
        recommendation = "We recommend speaking with a mental health professional. Our AI chat support is also available."
        buttons = [("AI Chat", "pages/3_Chat.py")]
    else:
        severity = "severe"
        color = "severity-severe"
        recommendation = "We strongly recommend immediate consultation with a mental health professional."
        buttons = [("Find Facilities", "pages/5_Facilities.py")]

    # Store current assessment
    st.session_state.last_assessment = {
        'date': datetime.now(),
        'severity': severity,
        'color': color,
        'recommendation': recommendation,
        'score': st.session_state.score,
        'percentage': score_percentage
    }

    st.markdown(f"""
        <div class="score-card">
            <h2>Assessment Complete</h2>
            <h3 class="{color}">Severity Level: {severity.title()}</h3>
            <p>{recommendation}</p>
        </div>
    """, unsafe_allow_html=True)

    # Display action buttons based on severity
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        for button_text, page in buttons:
            if st.button(button_text, use_container_width=True):
                st.switch_page(page)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='font-family: "Source Sans Pro", sans-serif;'>
    <h4 style='color: #7792E3;'>Assessment Guidelines:</h4>
    <ul style='color: #262730;'>
        <li>Answer all questions honestly</li>
        <li>Consider your experiences in recent weeks</li>
        <li>Take your time to reflect</li>
        <li>There are no right or wrong answers</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
