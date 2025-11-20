import aiohttp
import asyncio
import requests
from PIL import Image
from io import BytesIO
from langchain_google_genai import GoogleGenerativeAI
import streamlit as st
import os

# Initialize the Google Gemini LLM
# Note: We need to pass the API key here or ensure it's available in the environment
def get_llm(api_key):
    return GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)

def get_recipe(llm, dish_name):
    try:
        prompt = f"Provide a detailed, step-by-step recipe for {dish_name}. Include ingredients and instructions. Format it nicely with Markdown."
        response = llm.generate([prompt])
        return response.generations[0][0].text if response.generations else 'No recipe found.'
    except Exception as e:
        return f"Error fetching recipe: {e}"

async def fetch_youtube_links(dish_name, youtube_api_key):
    try:
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={dish_name}&key={youtube_api_key}&maxResults=3&type=video"
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                response_data = await response.json()
        
        if 'items' in response_data and response_data['items']:
            video_links = []
            for item in response_data['items']:
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                thumbnail = item['snippet']['thumbnails']['medium']['url']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                video_links.append({'title': title, 'url': video_url, 'thumbnail': thumbnail})
            return video_links
        else:
            return []
    except Exception as e:
        print(f"Error fetching YouTube links: {e}")
        return []

async def fetch_image(session, url):
    try:
        async with session.get(url, timeout=5) as img_response:
            if img_response.status == 200:
                content_type = img_response.headers.get('Content-Type')
                if content_type and 'image' in content_type and 'gif' not in content_type:
                    img_data = await img_response.read()
                    return Image.open(BytesIO(img_data))
    except Exception:
        return None
    return None

async def fetch_images(dish_name, google_api_key, search_engine_id):
    try:
        # Using Google Custom Search API
        search_url = f"https://www.googleapis.com/customsearch/v1?q={dish_name}&searchType=image&key={google_api_key}&cx={search_engine_id}&num=5"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                response_data = await response.json()
        
        images = []
        if 'items' in response_data:
            image_urls = [item['link'] for item in response_data['items']]
            
            async with aiohttp.ClientSession() as session:
                tasks = [fetch_image(session, url) for url in image_urls]
                results = await asyncio.gather(*tasks)
                images = [img for img in results if img is not None]
                
        return images[:4] # Return top 4 images for a nice grid
        
    except Exception as e:
        print(f"Error fetching images: {e}")
        return []

async def fetch_locations(dish_name, google_places_api_key):
    try:        
        places_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={dish_name}&key={google_places_api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(places_url) as response:
                places_data = await response.json()
        
        locations = []
        if 'results' in places_data:
            for place in places_data['results'][:5]:
                locations.append({
                    'name': place['name'],
                    'address': place.get('formatted_address', 'No address available'),
                    'rating': place.get('rating', 'N/A'),
                    'location': place['geometry']['location']
                })
        elif 'error_message' in places_data:
            st.error(f"Google Maps API Error: {places_data['error_message']}")
        
        return locations
    except Exception as e:
        print(f"Error fetching locations: {e}")
        return []
