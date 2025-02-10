import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import calendar
from pymongo import MongoClient
from itertools import groupby
from settings import settings

# Page configuration
st.set_page_config(
    page_title="MindfulAI - Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.logo(
    image="media/mainlogo.png",
    size="large"
)

# MongoDB connection
@st.cache_resource
def init_connection():
    return MongoClient(settings.DATABASE_HOST)

client = init_connection()
db = client[settings.DATABASE_NAME]
collection = db["user_data"]

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #e0e0ef;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .mood-emoji { font-size: 24px; margin-right: 10px; }
    .stButton > button { background-color: #7792E3 !important; color: white; font-weight: bold; }
    .chart-container { background-color: white; padding: 15px; border-radius: 10px; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# Mood mapping with emojis
MOODS = {
    "Happy": "😊",
    "Neutral": "😐",
    "Anxious": "😰",
    "Sad": "😢",
    "Depressed": "😔"
}

# Initialize session state
if 'current_user' not in st.session_state:
    users = collection.distinct("user_id")
    if users:
        st.session_state.current_user = users[0]
        st.session_state.start_date = datetime.now() - timedelta(days=30)
        st.session_state.end_date = datetime.now()

# Data loading function
@st.cache_data
def load_user_data(user_id, start_date, end_date):
    query = {
        "user_id": user_id,
        "date": {"$gte": start_date, "$lte": end_date}
    }
    docs = list(collection.find(query).sort("date", 1))
    
    if not docs:
        return None
        
    aggregated = {
        "mood_history": [m for doc in docs for m in doc["mood_history"]],
        "panic_episodes": [ep for doc in docs for ep in doc["panic_episodes"]],
        "chat_durations": [chat for doc in docs for chat in doc["chat_durations"]],
        "stressors": docs[-1]["stressors"],  # Latest entry
        "activity_impact": docs[-1]["activity_impact"]  # Latest entry
    }
    return aggregated

# Sidebar controls
with st.sidebar:    
    # User selection
    users = collection.distinct("user_id")
    if users:
        selected_user = st.selectbox("Select User", users, index=0)
        if selected_user != st.session_state.get('current_user'):
            st.session_state.current_user = selected_user
            st.rerun()
            
    # Date range selection
    start_date = st.date_input("Start Date", 
                              value=st.session_state.get('start_date', datetime.now() - timedelta(days=30)),
                              max_value=datetime.now())
    end_date = st.date_input("End Date", 
                            value=st.session_state.get('end_date', datetime.now()),
                            max_value=datetime.now())
    
    # Mood logging
    st.subheader("Daily Mood Check-in")
    selected_mood = st.selectbox("How are you feeling today?", list(MOODS.keys()))
    
    if st.button("Log Mood"):
        new_mood = {
            'timestamp': datetime.now(),
            'mood': selected_mood
        }
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        collection.update_one(
            {"user_id": st.session_state.current_user, "date": today},
            {"$push": {"mood_history": new_mood}},
            upsert=True
        )
        st.success(f"Mood logged: {MOODS[selected_mood]} {selected_mood}")
        st.rerun()

# Load data based on selections
if st.session_state.current_user:
    user_data = load_user_data(
        st.session_state.current_user,
        st.session_state.start_date,
        st.session_state.end_date
    )
else:
    user_data = None

# Main Dashboard
st.title("Mental Health Dashboard")

# Top Metrics Row
col1, col2, col3 = st.columns(3)
with col1:
    if user_data and user_data['mood_history']:
        mood_dates = sorted({m['timestamp'].date() for m in user_data['mood_history']})
        streak = 0
        current_streak = 0
        for i in range(1, len(mood_dates)):
            if (mood_dates[i] - mood_dates[i-1]).days == 1:
                current_streak += 1
                streak = max(streak, current_streak)
            else:
                current_streak = 0
        
        st.markdown(f"""
            <div class="metric-card">
                <h3>Current Mood Streak</h3>
                <h2>{streak} days</h2>
                <p>Longest consecutive check-in streak</p>
            </div>
        """, unsafe_allow_html=True)

with col2:
    if user_data:
        weekly_episodes = len([ep for ep in user_data['panic_episodes'] 
                             if ep > datetime.now() - timedelta(days=7)])
        st.markdown(f"""
            <div class="metric-card">
                <h3>Panic Episodes</h3>
                <h2>{weekly_episodes}</h2>
                <p>Last 7 days</p>
            </div>
        """, unsafe_allow_html=True)

with col3:
    if user_data and user_data['mood_history']:
        total_days = (datetime.now().date() - min([m['timestamp'].date() 
                                                  for m in user_data['mood_history']])).days + 1
        consistency = round(len({m['timestamp'].date() 
                               for m in user_data['mood_history']}) / total_days * 100, 1)
        st.markdown(f"""
            <div class="metric-card">
                <h3>Check-in Consistency</h3>
                <h2>{consistency}%</h2>
                <p>Last {total_days} days</p>
            </div>
        """, unsafe_allow_html=True)

# Charts Section
if user_data:
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Mood Trends")
        mood_df = pd.DataFrame(user_data['mood_history'])
        mood_df['date'] = mood_df['timestamp'].dt.date
        daily_moods = mood_df.groupby('date')['mood'].agg(lambda x: x.mode()[0]).reset_index()
        fig = px.line(daily_moods, x='date', y='mood', 
                     title="Daily Dominant Mood",
                     color_discrete_sequence=['#7792E3'])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Panic Episode Patterns")
        if user_data['panic_episodes']:
            hours = [ep.hour for ep in user_data['panic_episodes']]
            fig = px.histogram(x=hours, nbins=24,
                             title="Time of Day Distribution",
                             labels={'x': 'Hour of Day', 'y': 'Number of Episodes'},
                             color_discrete_sequence=['#7792E3'])
            st.plotly_chart(fig, use_container_width=True)

    # Activity Impact Analysis
    st.markdown("---")
    st.subheader("Activity Impact Analysis")
    if user_data['activity_impact']:
        activities = list(user_data['activity_impact'].keys())
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=activities,
            x=[v['positive'] for v in user_data['activity_impact'].values()],
            name='Positive Impact',
            orientation='h',
            marker_color='#7792E3'
        ))
        fig.add_trace(go.Bar(
            y=activities,
            x=[v['neutral'] for v in user_data['activity_impact'].values()],
            name='Neutral Impact',
            orientation='h',
            marker_color='#E3E3E3'
        ))
        fig.add_trace(go.Bar(
            y=activities,
            x=[v['negative'] for v in user_data['activity_impact'].values()],
            name='Negative Impact',
            orientation='h',
            marker_color='#FFB4B4'
        ))
        fig.update_layout(
            barmode='stack',
            height=400,
            xaxis_title="Impact Percentage",
            plot_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Monthly Calendar View
    st.markdown("---")
    st.subheader("Monthly Overview")
    current_month = datetime.now().month
    current_year = datetime.now().year

    month_calendar = calendar.monthcalendar(current_year, current_month)
    calendar_data = []
    for week in month_calendar:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append("")
            else:
                mood_entry = next((m for m in user_data['mood_history'] 
                              if m['timestamp'].day == day 
                              and m['timestamp'].month == current_month), None)
                week_data.append(f"{day} {MOODS[mood_entry['mood']]}" if mood_entry else f"{day}")
        calendar_data.append(week_data)

    df_calendar = pd.DataFrame(calendar_data, columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    st.table(df_calendar)
else:
    st.warning("No user data available. Please check your database connection.")
