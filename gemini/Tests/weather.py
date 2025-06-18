from google import genai
import json
import requests  # For API calls to the external tool

# Initialize the Google GenAI API
client = genai.Client(api_key='....')

# Define a function to interact with an external tool (in this case, a mock weather API)
def get_weather_data(location):
    print("Getting weather data from weatherapi...")
    """
    Function to get weather data from an external API
    """
    try:
        response = requests.get(f"https://api.weatherapi.com/v1/current.json?key=cfa6811dba9a4ea79c9132213251702&q={location}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Function to generate a response based on user's query and tool data
def generate_response(user_query, tool_data):
    # Create a prompt that includes the tool data
    prompt = f"""
User query: {user_query}
External tool data: {json.dumps(tool_data, indent=2)}

Based on the user query and the external tool data provided above, generate a helpful and informative response.
"""
    
    # Call Google's Generative AI model
    response = client.models.generate_content(
        model='gemini-2.0-flash-001', contents=prompt
    )
    
    return response.text

# Main chat function
def chat_with_user():
    print("Welcome to the AI assistant. Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        # Check if the user is asking about weather
        if "weather" in user_input.lower():
            print("Extract location from query (simplistic approach for demo)")
            words = user_input.lower().split()
            if "in" in words:
                location_index = words.index("in") + 1
                location = words[location_index] if location_index < len(words) else "New York"  # Default
            else:
                location = "New York"  # Default location
                
            # Get data from external tool
            weather_data = get_weather_data(location)
            
            # Generate response using GenAI and the tool data
            response = generate_response(user_input, weather_data)
        else:
            print("::For non-weather queries, just use GenAI directly")
            response = client.models.generate_content(
                model='gemini-2.0-flash-001', contents=user_input
            )
        
        print(f"\nAssistant: {response}")

# Run the chat function if this script is executed directly
if __name__ == "__main__":
    chat_with_user()