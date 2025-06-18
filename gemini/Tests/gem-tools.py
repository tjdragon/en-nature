from google import genai
from google.genai import types

def set_light_values(brightness: int, color_temp: str) -> dict[str, int | str]:
    print("Setting light values", brightness, color_temp)

    """Set the brightness and color temperature of a room light. (mock API).

    Args:
        brightness: Light level from 0 to 100. Zero is off and 100 is full brightness
        color_temp: Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.

    Returns:
        A dictionary containing the set brightness and color temperature.
    """
    return {
        "brightness": brightness,
        "colorTemperature": color_temp
    }

config = types.GenerateContentConfig(tools=[set_light_values])

GEMINI_API_KEY = "..."
client = genai.Client(api_key=GEMINI_API_KEY)

# Generate directly with generate_content.
response = client.models.generate_content(
    model='gemini-2.0-flash',
    config=config,
    contents='Turn the lights down to a romantic level'
)
print(response.text)

# Use the chat interface.
chat = client.chats.create(model='gemini-2.0-flash', config=config)
response = chat.send_message('Turn the lights down to a romantic level, like 20%, light red')
print(response.text)