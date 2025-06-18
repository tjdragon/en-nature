from google import genai
from google.genai import types
from serpapi import GoogleSearch

GEMINI_API_KEY = "..."
SERP_API_KEY = "...."

default_latitude = 46.207474
default_longitude = 6.138684
default_zoom_factor = "5z"

def search_for_restaurants(food_type: str) -> dict[str, int | str]:
    print("search_for_restaurants", food_type)

    """Searches for restaurants based on the food type and default latitude and longitude.

    Args:
        food_type: The food type to search for.

    Returns:
        A JSON formatted object with the local results 
    """

    where = f"@{default_latitude},{default_longitude},{default_zoom_factor}"
    params = {
        "engine": "google_maps",
        "q": food_type,
        "ll": where,
        "api_key": SERP_API_KEY
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()["local_results"]

    return results

config = types.GenerateContentConfig(tools=[search_for_restaurants])


client = genai.Client(api_key=GEMINI_API_KEY)

# Generate directly with generate_content.
response = client.models.generate_content(
    model='gemini-2.0-flash',
    config=config,
    contents='You are a personal assistant giving recommendations about restaurants'
)
print(response.text)

# Use the chat interface.
chat = client.chats.create(model='gemini-2.0-flash', config=config)
response = chat.send_message('Hi. I would like a Japanese ramen restaurant.')
print(response.text)