import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from api_services import get_llm, get_recipe, fetch_images, fetch_youtube_links, fetch_locations
from utils import get_user_location, inject_custom_css

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("GOOGLE_GEM_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")

# Page Config
st.set_page_config(
    page_title="Gourmet AI - Recipe Finder",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Custom CSS
inject_custom_css("styles.css")

# Initialize Session State
if 'chat' not in st.session_state:
    st.session_state.chat = get_llm(API_KEY)
if 'recipe' not in st.session_state:
    st.session_state.recipe = ""
if 'images' not in st.session_state:
    st.session_state.images = []
if 'youtube_links' not in st.session_state:
    st.session_state.youtube_links = []
if 'locations' not in st.session_state:
    st.session_state.locations = []
if 'has_searched' not in st.session_state:
    st.session_state.has_searched = False

def reset_app():
    st.session_state.recipe = ""
    st.session_state.images = []
    st.session_state.youtube_links = []
    st.session_state.locations = []
    st.session_state.has_searched = False

# Header
st.markdown("<h1>🍳 Gourmet AI <br><span style='font-size: 1.5rem; color: #666; font-weight: 400;'>Your Personal Culinary Assistant</span></h1>", unsafe_allow_html=True)

# Search Area
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        dish_name = st.text_input("What are you craving today?", placeholder="e.g., Truffle Mushroom Risotto")
        
        search_col1, search_col2 = st.columns(2)
        with search_col1:
            find_recipe_btn = st.button("👨‍🍳 Find Recipe & More")
        with search_col2:
            find_places_btn = st.button("📍 Find Restaurants Near Me")

# Logic for "Find Recipe"
if find_recipe_btn and dish_name:
    with st.spinner(f"Cooking up the best recipe for {dish_name}..."):
        reset_app()
        st.session_state.has_searched = True
        
        # Fetch Data concurrently
        async def fetch_all_data():
            recipe_task = asyncio.to_thread(get_recipe, st.session_state.chat, dish_name)
            images_task = fetch_images(dish_name, GOOGLE_API_KEY, SEARCH_ENGINE_ID)
            youtube_task = fetch_youtube_links(dish_name, YOUTUBE_API_KEY)
            
            return await asyncio.gather(recipe_task, images_task, youtube_task)

        results = asyncio.run(fetch_all_data())
        st.session_state.recipe = results[0]
        st.session_state.images = results[1]
        st.session_state.youtube_links = results[2]

# Logic for "Find Restaurants"
if find_places_btn and dish_name:
    with st.spinner(f"Scouting for {dish_name} nearby..."):
        st.session_state.locations = asyncio.run(fetch_locations(dish_name, GOOGLE_PLACES_API_KEY))

# Display Results
if st.session_state.has_searched or st.session_state.locations:
    
    # Layout: Recipe on Left, Visuals on Right
    content_col1, content_col2 = st.columns([3, 2])
    
    with content_col1:
        if st.session_state.recipe:
            st.markdown("### 📜 The Recipe")
            st.markdown(f"<div class='recipe-text'>{st.session_state.recipe}</div>", unsafe_allow_html=True)

    with content_col2:
        # Images Gallery
        if st.session_state.images:
            st.markdown("### 📸 Visuals")
            img_cols = st.columns(2)
            for idx, img in enumerate(st.session_state.images):
                with img_cols[idx % 2]:
                    st.image(img, use_column_width=True, output_format='JPEG')
        
        # YouTube Links
        if st.session_state.youtube_links:
            st.markdown("### 🎥 Watch & Cook")
            for video in st.session_state.youtube_links:
                st.markdown(f"""
                <a href="{video['url']}" target="_blank" class="video-link">
                    <img src="{video['thumbnail']}" class="video-thumbnail">
                    <span class="video-title">{video['title']}</span>
                </a>
                """, unsafe_allow_html=True)

    # Locations Section (Full Width)
    if st.session_state.locations:
        st.markdown("---")
        st.markdown("### 📍 Places Serving This Dish")
        
        user_lat, user_long = get_user_location(IPINFO_TOKEN)
        
        map_col, list_col = st.columns([2, 1])
        
        with map_col:
            st.markdown(f"""
                <iframe
                    width="100%"
                    height="400"
                    style="border:0; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
                    loading="lazy"
                    allowfullscreen
                    src="https://www.google.com/maps/embed/v1/search?key={GOOGLE_MAPS_API_KEY}&q={dish_name}&center={user_lat},{user_long}&zoom=12">
                </iframe>
            """, unsafe_allow_html=True)
            
        with list_col:
            for place in st.session_state.locations:
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <strong>{place['name']}</strong><br>
                    <span style="font-size: 0.9em; color: #666;">{place['address']}</span><br>
                    <span style="color: #f1c40f;">★ {place['rating']}</span>
                </div>
                """, unsafe_allow_html=True)

# Reset Button (Floating or at bottom)
st.markdown("---")
if st.button("🔄 Start Over"):
    reset_app()
    st.rerun()
