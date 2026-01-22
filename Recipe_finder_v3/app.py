import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from api_services import get_llm, get_recipe, fetch_images, fetch_youtube_links, fetch_locations
from utils import get_user_location, inject_custom_css

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("GROQ_API_KEY")
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
if 'searched_dish' not in st.session_state:
    st.session_state.searched_dish = ""

def reset_app():
    st.session_state.recipe = ""
    st.session_state.images = []
    st.session_state.youtube_links = []
    st.session_state.locations = []
    st.session_state.has_searched = False
    st.session_state.searched_dish = ""

# Header
st.markdown("<h1>🍳 Gourmet AI <br><span style='font-size: 1.5rem; color: #666; font-weight: 400;'>Your Personal Culinary Assistant</span></h1>", unsafe_allow_html=True)

# Search Area with Real-time Autocomplete
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        from autocomplete_component import autocomplete_search_box
        
        # 1. Get value from URL query parameters (set by our JS component)
        url_dish = st.query_params.get("dish", "")
        
        # 2. Render the autocomplete component
        # We don't use its return value anymore to avoid DeltaGenerator issues
        autocomplete_search_box(
            placeholder="What are you craving today?",
            key="dish_search"
        )
        
        # 3. Use the URL value as our source of truth
        current_dish = url_dish
        
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        search_col1, search_col2 = st.columns(2)
        with search_col1:
            find_recipe_btn = st.button("👨‍🍳 Find Recipe & More")
        with search_col2:
            find_places_btn = st.button("📍 Find Restaurants Near Me")

# Logic for "Find Recipe"
# Trigger if button is clicked OR if a dish was just selected via autocomplete (but NOT if Find Restaurants was clicked)
if find_recipe_btn or (current_dish and not st.session_state.has_searched and not find_places_btn):
    if current_dish:
        with st.spinner(f"Cooking up the best recipe for {current_dish}..."):
            # Store the dish name before resetting
            dish_to_search = current_dish
            reset_app()
            st.session_state.has_searched = True
            st.session_state.searched_dish = dish_to_search
            
            # Fetch Data concurrently
            async def fetch_all_data():
                recipe_task = asyncio.to_thread(get_recipe, st.session_state.chat, dish_to_search)
                images_task = fetch_images(dish_to_search, GOOGLE_API_KEY, SEARCH_ENGINE_ID)
                youtube_task = fetch_youtube_links(dish_to_search, YOUTUBE_API_KEY)
                
                return await asyncio.gather(recipe_task, images_task, youtube_task)

            results = asyncio.run(fetch_all_data())
            st.session_state.recipe = results[0]
            st.session_state.images = results[1]
            st.session_state.youtube_links = results[2]
            
            # Clear the URL query param so search box is ready for new search
            st.query_params.clear()
            st.rerun()
    elif find_recipe_btn:
        st.warning("Please enter a dish name first, then click Find Recipe.")

# Logic for "Find Restaurants"
if find_places_btn:
    # Use current_dish from URL, or fall back to previously searched dish
    dish_for_restaurants = current_dish or st.session_state.searched_dish
    
    if dish_for_restaurants:
        with st.spinner(f"Scouting for {dish_for_restaurants} nearby..."):
            st.session_state.searched_dish = dish_for_restaurants
            locations_result = asyncio.run(fetch_locations(dish_for_restaurants, GOOGLE_PLACES_API_KEY))
            st.session_state.locations = locations_result
            
            # Clear the URL query param so search box is ready for new search
            st.query_params.clear()
            
            # Only rerun if we got results
            if locations_result:
                st.rerun()
    else:
        st.warning("Please enter a dish name first (type and press Enter), then click Find Restaurants.")

# Display Results
if st.session_state.has_searched or st.session_state.locations:
    
    # Layout: Recipe on Left, Visuals on Right
    content_col1, content_col2 = st.columns([3, 2])
    
    with content_col1:
        if st.session_state.recipe:
            st.markdown(f"### 📜 Recipe for {st.session_state.searched_dish}")
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
        st.markdown(f"### 📍 Places Serving {st.session_state.searched_dish}")
        
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
                    src="https://www.google.com/maps/embed/v1/search?key={GOOGLE_MAPS_API_KEY}&q={st.session_state.searched_dish}&center={user_lat},{user_long}&zoom=12">
                </iframe>
            """, unsafe_allow_html=True)
            
        with list_col:
            for place in st.session_state.locations:
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <strong style="color: #333; font-size: 1.1em;">{place['name']}</strong><br>
                    <span style="font-size: 0.9em; color: #666;">{place['address']}</span><br>
                    <span style="color: #f1c40f;">★ {place['rating']}</span>
                </div>
                """, unsafe_allow_html=True)

# Reset Button
st.markdown("---")
if st.button("🔄 Start Over"):
    reset_app()
    # Clear query params
    st.query_params.clear()
    st.rerun()
