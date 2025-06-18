from serpapi import GoogleSearch

SERP_API_KEY = "..."

default_latitude = 46.207474
default_longitude = 6.138684
default_zoom_factor = "5z"
where = f"@{default_latitude},{default_longitude},{default_zoom_factor}"

params = {
        "engine": "google_maps",
        "q": "Japanese ramen",
        "ll": where,
        "api_key": SERP_API_KEY
    }

search = GoogleSearch(params)
results = search.get_dict()["local_results"]

print(results)