from google import genai
from google.genai import types

GEMINI_API_KEY = "AIz..."
GEMINI_MODEL = "gemini-2.0-flash"

system_instructions = ""
with open("system-instruction.txt", "r") as f:
    system_instructions = f.read()

client = genai.Client(api_key=GEMINI_API_KEY)

chat = client.chats.create(
    model=GEMINI_MODEL, 
    config=types.GenerateContentConfig(
        system_instruction=system_instructions,
        tools=[types.Tool(
            google_search=types.GoogleSearchRetrieval(
                dynamic_retrieval_config=types.DynamicRetrievalConfig(
                    dynamic_threshold=0.6))
        )]
    ))

print("Welcome. I am your IK Personal Assistant. How can I help?")
while(True):
    user_input = input("[U]-> ") # Looking for a japanese ramen restaurant
    response = chat.send_message(user_input)
    print("[G]->", response.text)