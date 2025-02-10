import streamlit as st
import webbrowser

# Page configuration
st.set_page_config(
    page_title="Soothify - Mental Health Blog",
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
    
    .blog-card {
        background-color: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
        height: 100%;
        cursor: pointer;
        margin: 0 10px 20px 10px;  /* Add margins around cards */
    }
    
    /* Add container for better spacing */
    .blog-container {
        padding: 15px;
        margin-bottom: 20px;
    }
    
    /* Adjust column spacing */
    [data-testid="stHorizontalBlock"] {
        gap: 20px;
        padding: 10px;
    }
    
    /* Make sure columns have proper spacing */
    [data-testid="column"] {
        padding: 0 10px;
    }    
    
    .blog-card:hover {
        transform: translateY(-5px);
    }
    
    .blog-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
    
    .blog-content {
        padding: 20px;
    }
    
    .blog-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1f1f1f;
        margin-bottom: 10px;
    }
    
    .blog-title:hover {
        color: #7792E3 !important;
    }

    a {
        text-decoration: none !important;
    }

    
    .blog-excerpt {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .blog-meta {
        margin-top: 15px;
        font-size: 0.8rem;
        color: #7792E3;
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
    </style>
""", unsafe_allow_html=True)

# Blog data
blogs = [
    {
        "title": "Understanding and Managing Panic Attacks",
        "image": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d",
        "excerpt": "Learn about the science behind panic attacks and effective coping strategies for managing them in your daily life.",
        "category": "Mental Health",
        "read_time": "5 min read",
        "url": "https://www.healthline.com/health/panic-attack",
        "date": "Feb 15, 2024"
    },
    {
        "title": "Mindfulness Techniques for Anxiety Relief",
        "image": "https://images.unsplash.com/photo-1506126613408-eca07ce68773",
        "excerpt": "Discover practical mindfulness exercises that can help reduce anxiety and promote mental well-being.",
        "category": "Wellness",
        "read_time": "4 min read",
        "url": "https://www.mindful.org/how-to-manage-anxiety-with-mindfulness/",
        "date": "Feb 14, 2024"
    },
    {
        "title": "Building a Strong Support System for Better Health",
        "image": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac",
        "excerpt": "The importance of social connections and how to build a supportive network for better mental health.",
        "category": "Relationships",
        "read_time": "6 min read",
        "url": "https://www.psychologytoday.com/us/basics/social-support",
        "date": "Feb 13, 2024"
    },
    {
        "title": "Sleep and Mental Health: The Vital Connection",
        "image": "https://images.unsplash.com/photo-1541480601022-2308c0f02487",
        "excerpt": "Explore the relationship between sleep quality and mental well-being, with practical tips for better sleep.",
        "category": "Health",
        "read_time": "7 min read",
        "url": "https://www.sleepfoundation.org/mental-health",
        "date": "Feb 12, 2024"
    },
    {
        "title": "Exercise as a Natural Stress Reliever",
        "image": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b",
        "excerpt": "How physical activity can improve mental health and reduce stress and anxiety levels.",
        "category": "Fitness",
        "read_time": "5 min read",
        "url": "https://www.mayoclinic.org/healthy-lifestyle/stress-management/in-depth/exercise-and-stress/art-20044469",
        "date": "Feb 11, 2024"
    },
    {
        "title": "Digital Detox for Mental Clarity",
        "image": "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2",
        "excerpt": "The benefits of taking breaks from technology and how to implement a healthy digital routine.",
        "category": "Lifestyle",
        "read_time": "4 min read",
        "url": "https://www.verywellmind.com/why-and-how-to-do-a-digital-detox-4771321",
        "date": "Feb 10, 2024"
    }
]

# Main content
st.markdown("<h1 class='section-title'>Mental Health Resources</h1>", unsafe_allow_html=True)

# Create rows of 3 blogs each
# Create rows of 3 blogs each
for i in range(0, len(blogs), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(blogs):
            blog = blogs[i + j]
            with cols[j]:
                st.markdown(f"""
                    <div class="blog-container">
                        <div class="blog-card">
                            <img src="{blog['image']}" class="blog-image" alt="{blog['title']}">
                            <div class="blog-content">
                                <a href="{blog['url']}" target="_blank" style="text-decoration: none;">
                                    <div class="blog-title" style="color: #1f1f1f; cursor: pointer; transition: color 0.2s ease;">
                                        {blog['title']}
                                    </div>
                                </a>
                                <div class="blog-excerpt">{blog['excerpt']}</div>
                                <div class="category-tag">{blog['category']}</div>
                                <div class="blog-meta">
                                    {blog['read_time']} • {blog['date']}
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    
    # Categories filter
    st.subheader("Categories")
    categories = list(set(blog['category'] for blog in blogs))
    selected_categories = st.multiselect("Filter by category", categories)
    
    # Search
    st.subheader("Search")
    search_term = st.text_input("Search blogs")
    
    # Reading time filter
    st.subheader("Reading Time")
    max_time = st.slider("Max reading time (minutes)", 1, 10, 10)
