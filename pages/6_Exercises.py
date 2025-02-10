import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Soothify - Mental Health Exercises",
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
    
    .main {
        background-color: #F0F2F5;
        font-family: 'Inter', sans-serif;
    }
    
    .exercise-card {
        background-color: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
        height: 100%;
        margin: 0 10px 20px 10px;
    }
    
    .exercise-container {
        padding: 15px;
        margin-bottom: 20px;
    }
    
    [data-testid="stHorizontalBlock"] {
        gap: 20px;
        padding: 10px;
    }
    
    [data-testid="column"] {
        padding: 0 10px;
    }
    
    .exercise-card:hover {
        transform: translateY(-5px);
    }
    
    .exercise-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
    
    .exercise-content {
        padding: 20px;
    }
    
    .exercise-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1f1f1f;
        margin-bottom: 10px;
    }
    
    .exercise-description {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 15px;
    }
    
    .exercise-steps {
        color: #444;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 15px 0;
        padding-left: 20px;
    }
    
    .exercise-meta {
        margin-top: 15px;
        font-size: 0.8rem;
        color: #7792E3;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .category-tag {
        background-color: #f0f2ff;
        color: #7792E3;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        display: inline-block;
        margin-top: 10px;
    }
    
    .section-title {
        font-size: 2rem;
        font-weight: 600;
        color: #1f1f1f;
        margin-bottom: 30px;
        text-align: center;
    }

    .stButton > button {
        background-color: #7792E3;
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        border: none;
        font-weight: 500;
        width: 100%;
        margin-top: 10px;
    }
    
    .stButton > button:hover {
        background-color: #6384dd;
    }
            
    .exercise-title:hover {
        color: #7792E3 !important;
    }

    a {
        text-decoration: none !important;
    }
        
    .exercise-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1f1f1f;
        margin-bottom: 10px;
        transition: color 0.2s ease;
    }

    </style>
""", unsafe_allow_html=True)

# Exercise data
exercises = [
    {
        "title": "4-7-8 Powerful Breathing Technique",
        "image": "https://images.unsplash.com/photo-1506126613408-eca07ce68773",
        "description": "A powerful relaxation technique that acts as a natural tranquilizer for the nervous system.",
        "benefits": [
            "Reduces anxiety and panic symptoms",
            "Helps with sleep issues",
            "Manages cravings and emotional responses"
        ],
        "category": "Breathing Exercise",
        "duration": "5 minutes",
        "difficulty": "Beginner",
        "url": "https://www.healthline.com/health/4-7-8-breathing"
    },
    
        {
        "title": "Progressive Muscle Relaxation",
        "image": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b",
        "description": "A systematic technique to release physical tension and reduce anxiety through muscle relaxation.",
        "benefits": [
            "Reduces physical tension",
            "Helps with anxiety and stress",
            "Improves body awareness",
            "Better sleep quality"
        ],
        "category": "Relaxation",
        "duration": "15 minutes",
        "difficulty": "Intermediate",
        "url": "https://www.healthline.com/health/progressive-muscle-relaxation"
    },
    {
        "title": "Grounding Technique 5-4-3-2-1",
        "image": "https://images.unsplash.com/photo-1499209974431-9dddcece7f88",
        "description": "An effective mindfulness exercise to manage anxiety and panic attacks by engaging your senses.",
        "benefits": [
            "Immediate anxiety relief",
            "Helps during panic attacks",
            "Brings focus to the present moment",
            "Easy to do anywhere"
        ],
        "category": "Mindfulness",
        "duration": "3 minutes",
        "difficulty": "Beginner",
        "url": "https://www.urmc.rochester.edu/behavioral-health-partners/bhp-blog/april-2018/5-4-3-2-1-coping-technique-for-anxiety.aspx"
    },
    {
        "title": "Body Scan Meditation",
        "image": "https://images.unsplash.com/photo-1545205597-3d9d02c29597",
        "description": "A mindful practice of systematically focusing attention on different parts of your body.",
        "benefits": [
            "Reduces physical tension",
            "Improves body awareness",
            "Helps with stress management",
            "Better sleep quality"
        ],
        "category": "Meditation",
        "duration": "10 minutes",
        "difficulty": "Intermediate",
        "url": "https://www.mindful.org/body-scan-meditation/"
    },
    {
        "title": "Safe Place Visualization",
        "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
        "description": "Create a mental sanctuary to find peace and calmness during stressful moments.",
        "benefits": [
            "Immediate stress relief",
            "Helps manage anxiety",
            "Creates a mental safe space",
            "Accessible anywhere"
        ],
        "category": "Visualization",
        "duration": "7 minutes",
        "difficulty": "Beginner",
        "url": "https://www.therapistaid.com/therapy-guide/visualization-guide"
    },
    {
        "title": "Mindful Walking",
        "image": "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8",
        "description": "A moving meditation that combines gentle walking with mindful awareness.",
        "benefits": [
            "Combines exercise with meditation",
            "Reduces anxiety and stress",
            "Improves physical awareness",
            "Helps clear the mind"
        ],
        "category": "Movement",
        "duration": "10 minutes",
        "difficulty": "Beginner",
        "url": "https://www.mindful.org/how-to-do-walking-meditation/"
    }
]

# Main content
st.markdown("<h1 class='section-title'>Mental Health Exercises</h1>", unsafe_allow_html=True)

# Create rows of 3 exercises each
# Create rows of 3 exercises each
for i in range(0, len(exercises), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(exercises):
            exercise = exercises[i + j]
            with cols[j]:
                st.markdown(f"""
                    <div class="exercise-container">
                        <div class="exercise-card">
                            <img src="{exercise['image']}" class="exercise-image" alt="{exercise['title']}">
                            <div class="exercise-content">
                                <a href="{exercise['url']}" target="_blank" style="text-decoration: none;">
                                    <div class="exercise-title" style="color: #1f1f1f; cursor: pointer; transition: color 0.2s ease;">
                                        {exercise['title']}
                                    </div>
                                </a>
                                <div class="exercise-description">{exercise['description']}</div>
                                <div class="category-tag">{exercise['category']}</div>
                                <div class="exercise-meta">
                                    ⏱️ {exercise['duration']} • 📊 {exercise['difficulty']}
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:    
    # Filters
    st.subheader("Filter Exercises")
    
    # Duration filter
    duration_filter = st.slider("Duration (minutes)", 0, 20, (0, 20))
    
    # Difficulty filter
    difficulties = ["Beginner", "Intermediate", "Advanced"]
    selected_difficulty = st.multiselect("Difficulty Level", difficulties)
    
    # Category filter
    categories = list(set(exercise['category'] for exercise in exercises))
    selected_categories = st.multiselect("Exercise Type", categories)
