import requests
import json

def get_suggestions(query):
    """
    Get autocomplete suggestions from Google using their autocomplete API
    This mimics Google's search suggestions
    """
    if not query or len(query) < 2:
        return []
    
    try:
        # Google's autocomplete API endpoint (publicly accessible)
        url = "http://suggestqueries.google.com/complete/search"
        
        params = {
            'client': 'firefox',  # or 'chrome'
            'q': f"{query} recipe",  # Add 'recipe' to get food-related suggestions
            'hl': 'en'  # Language
        }
        
        response = requests.get(url, params=params, timeout=2)
        
        if response.status_code == 200:
            # The response is in JSON format: [query, [suggestions]]
            data = response.json()
            
            if len(data) > 1 and isinstance(data[1], list):
                # Clean up suggestions - remove 'recipe' suffix if present
                suggestions = []
                for suggestion in data[1][:5]:  # Get top 5
                    # Remove ' recipe' from the end to show just the dish name
                    clean_suggestion = suggestion.replace(' recipe', '').strip()
                    # Capitalize first letter of each word
                    clean_suggestion = clean_suggestion.title()
                    suggestions.append(clean_suggestion)
                
                return suggestions
        
        return []
        
    except Exception as e:
        print(f"Error fetching autocomplete suggestions: {e}")
        # Fallback to empty list if API fails
        return []
