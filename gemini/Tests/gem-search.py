from google import genai
from google.genai import types

# https://ai.google.dev/gemini-api
GEMINI_API_KEY = "..."

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents="List of ramen restaurants near location Geneva train station. Provide details about the top 5 results, including reviews and location",
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            google_search=types.GoogleSearchRetrieval(
                dynamic_retrieval_config=types.DynamicRetrievalConfig(
                    dynamic_threshold=0.6))
        )]
    )
)
print("RESPONSE", response)

print("PARTS")
for each in response.candidates[0].content.parts:
    print(each.text)