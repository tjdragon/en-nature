import googlemaps  # For Google Maps integration

# https://developers.google.com/maps/get-started#create-project
MAPS_API_KEY = "..." 
gmaps = googlemaps.Client(key=MAPS_API_KEY)

places_result = gmaps.places(
    query="ramen places near Geneva",
    location="Geneva",
    type="restaurant",  # Specify restaurant type
    radius=5000,  # Search radius in meters (adjust as needed)
)

restaurants = []
if places_result["status"] == "OK":
    for place in places_result["results"]:
        place_id = place["place_id"]
        place_details = gmaps.place(place_id, fields=["name", "formatted_address", "rating", "website", "formatted_phone_number", "opening_hours"]) # Get details
        if place_details["status"] == "OK": # Handle potential errors when fetching details
            restaurant_info = place_details["result"]
            restaurants.append(restaurant_info)
        else:
            print(f"Error fetching details for place ID {place_id}: {place_details['status']}") #Print error message
    else:
        print(f"Error searching for restaurants: {places_result['status']}") #Print error message

if restaurants:
    recommendations_text = "Here are some restaurant recommendations based on your preferences:\n\n"
    for i, restaurant in enumerate(restaurants):
        recommendations_text += f"{i+1}. {restaurant.get('name', 'N/A')}\n"
        recommendations_text += f"   Address: {restaurant.get('formatted_address', 'N/A')}\n"
        recommendations_text += f"   Rating: {restaurant.get('rating', 'N/A')}\n"
        if restaurant.get('website'):
            recommendations_text += f"   Website: {restaurant.get('website')}\n"
        if restaurant.get('formatted_phone_number'):
            recommendations_text += f"   Phone: {restaurant.get('formatted_phone_number')}\n"
            
        if restaurant.get('opening_hours'):
            recommendations_text += f"   Open Now: {'Yes' if restaurant['opening_hours'].get('open_now') else 'No'}\n"
            recommendations_text += "\n"
    print(recommendations_text)
