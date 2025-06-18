from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import json
import requests
import time
import logging
import traceback


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='mvp_places.log',
    filemode='w'
)
logger = logging.getLogger(__name__)


load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"

logger.info(f"GOOGLE_MAPS_API_KEY present: {bool(GOOGLE_MAPS_API_KEY)}")
logger.info(f"GEMINI_API_KEY present: {bool(GEMINI_API_KEY)}")
logger.info(f"Using Gemini model: {GEMINI_MODEL}")


# 
# Uses the Google Maps Places API to search for places based on a query and fetch detailed information for each place
# This is the most accurate way to get up-to-date information about places
#
def search_places_with_details(query, max_results=20, api_key=GOOGLE_MAPS_API_KEY):
    logger.info(f"search_places_with_details called with query: '{query}', max_results: {max_results}")
    
    if not api_key:
        logger.error("Error: Google Maps API key not found")
        return "Error: Google Maps API key not found. Please set GOOGLE_MAPS_API_KEY in your .env file.", []

    base_url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.businessStatus,places.generativeSummary.overview,places.generativeSummary.description,nextPageToken"
    }
    
    all_results = []
    raw_results = []
    page_size = min(max_results, 20)
    page_token = None
    
    try:
        while len(all_results) < max_results:

            request_body = {
                "textQuery": query,
                "pageSize": page_size
            }

            if page_token:
                request_body["pageToken"] = page_token
            
            logger.debug(f"Making Maps API request with body: {json.dumps(request_body)}")
            
            response = requests.post(base_url, headers=headers, json=request_body)
            
            logger.debug(f"Maps API response status code: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Maps API error: HTTP {response.status_code} - {response.text}")
                if all_results:
                    break
                else:
                    return f"Error: HTTP Error {response.status_code} - {response.text}", []
            
            result_data = response.json()
            logger.debug(f"Maps API response keys: {list(result_data.keys())}")
            
            if "places" not in result_data:
                logger.warning("No 'places' found in the Maps API response")
                break
            
            logger.info(f"Found {len(result_data.get('places', []))} places in response")
            
            new_results = [place for place in result_data.get("places", []) 
                          if place.get('businessStatus') == 'OPERATIONAL']
            
            logger.info(f"Filtered to {len(new_results)} operational places")
            all_results.extend(new_results)
            
            page_token = result_data.get("nextPageToken")
            logger.debug(f"Next page token present: {bool(page_token)}")
            
            if not page_token or len(all_results) >= max_results:
                break
            
            logger.debug("Waiting 2 seconds before next page request")
            time.sleep(2)
        
        all_results = all_results[:max_results]
        logger.info(f"Final result count: {len(all_results)}")
        
        if not all_results:
            logger.warning("No places found matching search criteria")
            return "No places found matching your search criteria.", []
        
        output = []
        output.append(f"Found {len(all_results)} operational places matching: '{query}'\n")
        
        for i, place in enumerate(all_results, 1):
            place_id = place.get('id')
            
            overview = ""
            if 'generativeSummary' in place and 'overview' in place['generativeSummary']:
                overview = place['generativeSummary']['overview'].get('text', '')
                
            description = ""
            if 'generativeSummary' in place and 'description' in place['generativeSummary']:
                description = place['generativeSummary']['description'].get('text', '')
            
            logger.debug(f"Fetching details for place ID: {place_id}")
            place_details = get_place_details_raw(place_id, api_key)
            
            if isinstance(place_details, str) and place_details.startswith("Error"):
                logger.warning(f"Error fetching details for place ID {place_id}: {place_details}")
                output.append(f"==================== {i}. Place ID: {place_id} ====================")
                output.append(f"Could not retrieve details: {place_details}")
                output.append("")
                continue
            
            place_name = place_details.get('displayName', {}).get('text', f'Place ID: {place_id}')
            
            raw_results.append(place_details)
            
            output.append(f"==================== {i}. {place_name} ====================")
            
            if overview:
                output.append(f"Quick overview: {overview}")
            if description:
                output.append(f"Description: {description}")
                
            details_output = format_place_details(place_details)
            output.append(details_output)
            output.append("")
        
        formatted_results = "\n".join(output)
        logger.debug(f"Formatted results (first 500 chars): {formatted_results[:500]}...")
        
        return formatted_results, raw_results
    
    except Exception as e:
        error_msg = f"Exception in search_places_with_details: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return error_msg, []


#
# Fetches detailed information for a place using the Google Maps Places API
#
def get_place_details_raw(place_id, api_key=GOOGLE_MAPS_API_KEY):
    logger.debug(f"get_place_details_raw called for place_id: {place_id}")
    
    if not api_key:
        logger.error("Error: Google Maps API key not found")
        return "Error: Google Maps API key not found."
    
    base_url = f"https://places.googleapis.com/v1/places/{place_id}"
    
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "displayName,formattedAddress,location,rating,userRatingCount,websiteUri,nationalPhoneNumber,internationalPhoneNumber,priceLevel,servesBreakfast,servesLunch,servesDinner,servesBeer,servesWine,servesCocktails,servesCoffee,currentOpeningHours,regularOpeningHours,utcOffsetMinutes,accessibilityOptions,takeout,delivery,dineIn,reservable,shortFormattedAddress,editorialSummary,paymentOptions,addressComponents"
    }
    
    try:
        response = requests.get(base_url, headers=headers)
        
        logger.debug(f"Place details API response status code: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f"Error: HTTP Error {response.status_code} - {response.text}"
            logger.error(error_msg)
            return error_msg
        
        return response.json()
    except Exception as e:
        error_msg = f"Exception in get_place_details_raw: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return error_msg

#
# Formats the detailed information for a place into a human-readable format
#
def format_place_details(place_details):
    if isinstance(place_details, str) and place_details.startswith("Error"):
        return place_details
    
    output = []
    
    output.append(f"Address: {place_details.get('formattedAddress')}")
    
    if 'location' in place_details:
        location = place_details['location']
        output.append(f"Location: {location.get('latitude')}, {location.get('longitude')}")
    
    if 'internationalPhoneNumber' in place_details:
        output.append(f"International Phone: {place_details.get('internationalPhoneNumber')}")
    
    if 'nationalPhoneNumber' in place_details:
        output.append(f"National Phone: {place_details.get('nationalPhoneNumber')}")
    
    if 'websiteUri' in place_details:
        output.append(f"Website: {place_details.get('websiteUri')}")
    
    if 'rating' in place_details:
        output.append(f"Rating: {place_details.get('rating')} ({place_details.get('userRatingCount', 0)} reviews)")
    
    if 'priceLevel' in place_details:
        price_level = place_details.get('priceLevel')
        if isinstance(price_level, str):
            if "INEXPENSIVE" in price_level:
                price_str = "€"
            elif "MODERATE" in price_level:
                price_str = "€€"
            elif "EXPENSIVE" in price_level:
                price_str = "€€€"
            elif "VERY_EXPENSIVE" in price_level:
                price_str = "€€€€"
            else:
                price_str = price_level
        elif price_level is not None:
            try:
                price_str = "€" * int(price_level)
            except (ValueError, TypeError):
                price_str = str(price_level)
        else:
            price_str = "Price not specified"
        output.append(f"Price Level: {price_str}")
    
    if 'regularOpeningHours' in place_details:
        hours = place_details.get('regularOpeningHours', {})
        if 'weekdayDescriptions' in hours:
            output.append("\nOpening Hours:")
            for day in hours.get('weekdayDescriptions', []):
                output.append(f"  {day}")
    
    food_options = []
    if place_details.get('servesBreakfast'):
        food_options.append("Breakfast")
    if place_details.get('servesLunch'):
        food_options.append("Lunch")
    if place_details.get('servesDinner'):
        food_options.append("Dinner")
    if place_details.get('servesBrunch'):
        food_options.append("Brunch")
    if place_details.get('servesVegetarianFood'):
        food_options.append("Vegetarian")
    
    if food_options:
        output.append(f"\nServes: {', '.join(food_options)}")
    
    service_options = []
    if place_details.get('dineIn'):
        service_options.append("Dine-in")
    if place_details.get('takeout'):
        service_options.append("Takeout")
    if place_details.get('delivery'):
        service_options.append("Delivery")
    if place_details.get('reservable'):
        service_options.append("Reservations")
    
    if service_options:
        output.append(f"Service Options: {', '.join(service_options)}")
    
    if 'paymentOptions' in place_details:
        payment = place_details.get('paymentOptions', {})
        payment_methods = []
        
        if payment.get('acceptsCreditCards'):
            payment_methods.append("Credit Cards")
        if payment.get('acceptsDebitCards'):
            payment_methods.append("Debit Cards")
        if payment.get('acceptsCashOnly'):
            payment_methods.append("Cash Only")
        if payment.get('acceptsNfc'):
            payment_methods.append("NFC Payments")
        
        if payment_methods:
            output.append(f"Payment Methods: {', '.join(payment_methods)}")
    
    if 'accessibilityOptions' in place_details:
        access = place_details.get('accessibilityOptions', {})
        access_options = []
        
        if access.get('wheelchairAccessibleEntrance'):
            access_options.append("Wheelchair Accessible Entrance")
        if access.get('wheelchairAccessibleParking'):
            access_options.append("Wheelchair Accessible Parking")
        if access.get('wheelchairAccessibleRestroom'):
            access_options.append("Wheelchair Accessible Restroom")
        if access.get('wheelchairAccessibleSeating'):
            access_options.append("Wheelchair Accessible Seating")
        
        if access_options:
            output.append(f"Accessibility: {', '.join(access_options)}")
    
    return "\n".join(output)

#
# Schema for the search_places_with_details function
# 
places_search_schema = {
    "name": "search_places_with_details",
    "description": "Search for places using Google Maps Places API based on user query and fetch detailed information for each place",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query for Google Maps (e.g. 'Italian restaurants in Geneva')"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 5)"
            }
        },
        "required": ["query"]
    }
}

#
# The system prompt for the chat
#
SYSTEM_PROMPT = """
You are a friendly, helpful, and engaging personal assistant who specializes in recommending restaurants. Your mission is to provide personalized dining suggestions based on the user's preferences—whether that involves a specific cuisine, dietary needs, budget, or desired atmosphere.

THE CURRENT LOCATION OF THE USER :
- The DEFAULT location of the USER is the Flatiron Building in New York. IF the user specifies another location, use that instead.

Key Instructions:
1. ALWAYS USE THE search_places_with_details FUNCTION when the user asks for restaurant or dining recommendations. This is your only source of current, accurate restaurant data.
2. Engage in a warm, conversational, and natural manner. Use friendly and supportive language to build rapport.
3. Listen carefully to the user's preferences. Ask clarifying questions such as:
   - "What type of cuisine are you in the mood for today?"
   - "Do you have any dietary restrictions or a preferred budget?"
   - "Which area would you like to explore?"
4. When making a recommendation, immediately construct a query (e.g., "Italian restaurants near the Flatiron Building, New York" or "Japanese ramen near the Flatiron Building, New York" if no other location is provided) and call the search_places_with_details function.
5. Present multiple restaurant options that include the restaurant name and a brief description of the cuisine.
6. If no exact match is found, politely suggest broadening the search criteria.
7. If the user asks specifically for InKind partner restaurants, then ensure that the query passed to the tool includes that criterion (e.g., "InKind partner Italian restaurants near the Flatiron Building, New York").

Formatting Instructions:
- Your final answer must be detailed and presented in a human-friendly, multi-line format. Use bullet points or separate lines for key details.
- Avoid providing a single, long paragraph. Each detail should be on its own line or clearly separated so that it is easy to read.


TOOL: search_places_with_details
Description:
This function performs a comprehensive restaurant search using the Google Maps Places API. When provided with a query string that combines cuisine type and location (e.g., "Italian restaurants near the Flatiron Building, New York"), it returns a formatted string containing detailed information about each matching restaurant. The output includes key details such as the restaurant name, a brief description of the cuisine, address, ratings, price range, and other relevant information.
Usage:
- Call the function as: search_places_with_details(query, max_results=5)
- Parameters:
   • query (string): A text search string that includes the type of cuisine and the location. If the user requests InKind partner restaurants, include that in the query (e.g., "InKind partner Italian restaurants near the Flatiron Building, New York").
   • max_results (integer, optional): The maximum number of restaurants to return. Default is 5.
Expected Output:
- A formatted string with comprehensive details for each restaurant, including the restaurant name and a brief description of its cuisine.
- If no matching restaurants are found, an appropriate message indicating that no results were found.

Example Conversation Flow 1:
User: "I'm looking for a nice dinner spot tonight."
You: "That sounds exciting! What kind of cuisine are you in the mood for, and is there a particular area you'd like to explore?"
User: "I'm in the mood for Italian, somewhere downtown."
You: [Immediately call search_places_with_details with the query "Italian restaurants near the Flatiron Building, New York" or use the provided location if specified]
Then say: "Based on my search, I've found several charming Italian spots. For instance, one restaurant is known for its authentic pasta and cozy atmosphere, while another offers a relaxed vibe perfect for dinner. Would you like more details on any of these options?"

Example Conversation Flow 2 (InKind Partners):
User: "Do you have any InKind partners around here?"
You: "Absolutely! Are you looking for InKind partner restaurants near your current location, which is around the Flatiron Building in New York, or is there another area you're interested in?"
User: "I'm happy with my current area."
You: [Immediately call search_places_with_details with the query "InKind partner restaurants near the Flatiron Building, New York"]
Then say: "Based on my search, I've found some great InKind partner restaurants nearby. One option offers a modern twist on classic dishes, and another is celebrated for its farm-to-table ingredients. Would you like more details on any of these options?"

Remember: Your recommendations must always come from real-time data provided by the search_places_with_details tool. Let's make every dining decision a delightful experience!
"""

try:
    logger.info("Initializing Gemini client")
    client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("Gemini client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Gemini client: {str(e)}")
    logger.error(traceback.format_exc())
    raise

try:
    logger.info("Creating chat with tools configuration")
    
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[
            types.Tool(
                function_declarations=[places_search_schema]
            )
        ]
    )
    
    chat = client.chats.create(
        model=GEMINI_MODEL,
        config=config
    )
    
    logger.info("Chat created successfully with enhanced function calling configuration")
except Exception as e:
    logger.error(f"Error creating chat: {str(e)}")
    logger.error(traceback.format_exc())
    raise

print("Welcome. I am your InKind Personal Assistant. How can I help?")

context = {
    "last_query_type": None,
    "cuisine_mentioned": None, 
    "location_mentioned": None
}

while True:
    try:
        user_input = input("[U]-> ")
        logger.info(f"User input: '{user_input}'")
        
        lower_input = user_input.lower()
        
        cuisine_terms = ["japanese", "italian", "chinese", "indian", "french", "thai", "mexican", "ramen", "sushi", "pizza", "burger"]
        for term in cuisine_terms:
            if term in lower_input:
                context["cuisine_mentioned"] = term
                logger.info(f"Tracked cuisine mention: {term}")
                break
                
        if any(loc in lower_input for loc in ["near", "in", "at", "around", "close to"]):
            location_parts = []
            for word in user_input.split():
                if word.lower() in ["near", "in", "at", "around", "close"]:
                    location_start_idx = user_input.split().index(word) + 1
                    location_parts = user_input.split()[location_start_idx:]
                    break
                    
            if location_parts:
                context["location_mentioned"] = " ".join(location_parts)
                logger.info(f"Tracked location mention: {context['location_mentioned']}")
        
        logger.info(f"Current conversation context: {context}")
        
        logger.info("Sending message to Gemini with function calling enabled")
        response = chat.send_message(user_input)
        logger.info("Received response from Gemini")
        
        logger.debug(f"Response type: {type(response)}, attributes: {dir(response)}")
        
        has_function_call = False
        
        if hasattr(response, 'candidates') and response.candidates:
            logger.debug(f"Response has {len(response.candidates)} candidates")
            
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content:
                    content = candidate.content
                    
                    if hasattr(content, 'parts') and content.parts:
                        for part in content.parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                has_function_call = True
                                function_call = part.function_call
                                logger.info(f"Function call detected: {function_call.name}")
                                
                                if function_call.name == "search_places_with_details":
                                    args = function_call.args
                                    query = args.get("query", "")
                                    max_results = args.get("max_results", 20)
                                    
                                    logger.info(f"Executing search_places_with_details with query: '{query}', max_results: {max_results}")
                                    search_result, raw_data = search_places_with_details(query, max_results)
                                    
                                    logger.info("Sending function result back to Gemini")
                                    try:
                                        response = chat.send_message(search_result)
                                    except Exception as e:
                                        logger.error(f"Error sending function response: {str(e)}")
                                        try:
                                            response = chat.send_message(f"Here are the search results: {search_result}")
                                            logger.info("Successfully sent search results as text message")
                                        except Exception as e2:
                                            logger.error(f"Error sending text response: {str(e2)}")
                                            print(f"[G]-> I found some restaurant information but had trouble formatting it. Here's what I found:\n{search_result}")
                                            continue
                                    
                                    if hasattr(response, 'text') and response.text:
                                        print("[G]->", response.text)
                                        logger.info("Displayed response with function results to user")
                                    elif hasattr(response, 'candidates') and response.candidates:
                                        for candidate in response.candidates:
                                            if hasattr(candidate, 'content') and candidate.content:
                                                if hasattr(candidate.content, 'parts'):
                                                    for part in candidate.content.parts:
                                                        if hasattr(part, 'text') and part.text:
                                                            print("[G]->", part.text)
                                                            logger.info("Displayed text part from candidate")
                                                            break
                                    else:
                                        print("[G]-> I found some restaurant options for you. Let me know if you'd like more specific details.")
                                        logger.warning("No text response found after function execution")
        
        if not has_function_call:
            if hasattr(response, 'text') and response.text:
                print("[G]->", response.text)
                logger.info("Displayed direct text response to user")
            elif hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    print("[G]->", part.text)
                                    logger.info("Displayed text part from candidate")
                                    break
            else:
                print("[G]-> I'm processing your request. Could you please provide more details?")
                logger.warning("No text response found in direct response")
        
        response_text = ""
        if hasattr(response, 'text') and response.text:
            response_text = response.text
        elif hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text = part.text
                                break
        
        if response_text and ("where are you" in response_text.lower() or "what area" in response_text.lower()):
            context["last_query_type"] = "location"
            logger.info("Detected location query from assistant")
        
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected, exiting")
        print("\nExiting...")
        break
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"[ERROR]-> {str(e)}")
