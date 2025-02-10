import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Page configuration
st.set_page_config(
    page_title="Soothify - Nearby Facilities",
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
    
    .facility-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .contact-button {
        background-color: #7792E3;
        color: white;
        padding: 8px 16px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Emergency information
with st.sidebar:
    st.markdown("""
        <div style='background-color: #FFE8E6; padding: 20px; border-radius: 10px; margin-top: 20px;'>
            <h4 style='color: #EF5350;'>🚨 In case of emergency</h4>
            <p>If you're experiencing a mental health emergency, please:</p>
            <ul>
                <li>Call emergency services (911)</li>
                <li>Contact the National Crisis Hotline: 988</li>
                <li>Visit the nearest emergency room</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Sample database of mental health facilities (in real implementation, this would come from a proper database)
facilities_db = {
    'facilities': [
        {
            'name': 'Mental Health Center A',
            'address': '123 Health St',
            'phone': '(555) 123-4567',
            'services': ['Counseling', 'Psychiatry', 'Group Therapy'],
            'emergency': True
        },
        {
            'name': 'Wellness Clinic B',
            'address': '456 Care Ave',
            'phone': '(555) 987-6543',
            'services': ['Individual Therapy', 'Crisis Intervention'],
            'emergency': False
        }
    ]
}

def get_coordinates_from_pincode(pincode):
    """Get coordinates from pincode using Nominatim"""
    geolocator = Nominatim(user_agent="mental_health_app")
    try:
        location = geolocator.geocode(str(pincode))
        if location:
            return (location.latitude, location.longitude)
        return None
    except:
        return None

def find_nearby_facilities(user_coords, max_distance=10):
    """Find facilities within max_distance km of user_coords"""
    nearby = []
    for facility in facilities_db['facilities']:
        # In a real implementation, each facility would have its coordinates stored
        # Here we're just simulating nearby facilities
        nearby.append(facility)
    return nearby

# Main content
st.title("Find Mental Health Facilities Near Your Locality")

# Input section
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div style='background-color: white; padding: 20px; border-radius: 10px;'>
            <h4>Enter your location details</h4>
    """, unsafe_allow_html=True)
    
    pincode = st.text_input("Enter your pincode")
    search_radius = st.slider("Search radius (km)", 1, 50, 10)
    
    if st.button("Find Facilities", use_container_width=True):
        if pincode:
            coordinates = get_coordinates_from_pincode(pincode)
            if coordinates:
                st.session_state.user_coords = coordinates
                st.session_state.nearby_facilities = find_nearby_facilities(coordinates, search_radius)
                st.rerun()
            else:
                st.error("Invalid pincode. Please try again.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Display results
if 'nearby_facilities' in st.session_state and st.session_state.nearby_facilities:
    st.markdown("### Nearby Facilities")
    
    # Create map
    m = folium.Map(location=st.session_state.user_coords, zoom_start=12)
    
    # Add user location marker
    folium.Marker(
        st.session_state.user_coords,
        popup="Your Location",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)
    
    # Display facilities
    for facility in st.session_state.nearby_facilities:
        st.markdown(f"""
            <div class="facility-card">
                <h4>{facility['name']}</h4>
                <p>📍 {facility['address']}</p>
                <p>📞 {facility['phone']}</p>
                <p>🏥 Services: {', '.join(facility['services'])}</p>
                {'<p style="color: #EF5350;">🚨 24/7 Emergency Services Available</p>' if facility['emergency'] else ''}
                <a href="tel:{facility['phone']}" class="contact-button">Contact Facility</a>
            </div>
        """, unsafe_allow_html=True)
        
        # Add facility marker to map (in real implementation, use actual coordinates)
        folium.Marker(
            [st.session_state.user_coords[0] + 0.01, st.session_state.user_coords[1] + 0.01],
            popup=facility['name'],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
    
    # Display map
    st.markdown("### Facility Locations")
    folium_static(m)


