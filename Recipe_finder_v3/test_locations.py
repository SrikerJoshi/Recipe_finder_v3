import asyncio
import os
from dotenv import load_dotenv
from api_services import fetch_locations
from utils import get_user_location

load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")

async def test():
    print(f"Testing with Places Key: {GOOGLE_PLACES_API_KEY[:5]}...")
    print(f"Testing with IPInfo Token: {IPINFO_TOKEN[:5]}...")

    print("\nFetching locations for 'Sushi'...")
    # We need to modify api_services.py temporarily or copy the logic here to see the response
    # Let's copy the logic here for debugging
    import aiohttp
    places_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=Sushi&key={GOOGLE_PLACES_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(places_url) as response:
            data = await response.json()
            print(f"API Response: {data}")
            
    locations = await fetch_locations("Sushi", GOOGLE_PLACES_API_KEY)
    print(f"Found {len(locations)} locations.")
    if locations:
        print(locations[0])
    else:
        print("No locations found. Check API key or quota.")

    print("\nFetching user location...")
    lat, long = get_user_location(IPINFO_TOKEN)
    print(f"User Location: {lat}, {long}")

if __name__ == "__main__":
    asyncio.run(test())
