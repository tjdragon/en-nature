import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from streamlit_geolocation import streamlit_geolocation

# --- Load environment variables and configure Gemini ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("No GOOGLE_API_KEY found in .env file")

genai.configure(api_key=GOOGLE_API_KEY)

# --- Model Configuration (with Temperature) ---
generation_config = genai.GenerationConfig(
    temperature=0.7,
)

model = genai.GenerativeModel('gemini-2.0-flash')

# --- Load System Prompt ---
with open("prompt-tj.txt", "r") as f:
    system_prompt_template = f.read()

# --- Restaurant List (Placeholder - Replace or load from file/DB) ---
restaurant_list = []

restaurant_list_json = json.dumps(restaurant_list)
system_prompt = system_prompt_template.format(restaurant_list_json=restaurant_list_json)

# --- Streamlit App ---
st.title("Restaurant Recommendation Chatbot")

# --- Initialize States ---
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = False
if 'chat_started' not in st.session_state:
    st.session_state['chat_started'] = False
if 'location' not in st.session_state:
    st.session_state['location'] = None
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- Automatic Location Detection on First Load ---
if not st.session_state['initialized']:
    st.session_state['initialized'] = True
    st.rerun()  # Forces a rerun on first load to trigger geolocation

# --- Location Handling ---
location = streamlit_geolocation()

col1, col2 = st.columns([3, 1])

with col1:
    if location and isinstance(location, dict) and location.get("latitude") and location.get("longitude"):
        st.session_state['location'] = location
        st.success(f"📍 Location detected: {location['latitude']:.6f}, {location['longitude']:.6f}")
        
        # Optionally, you could display a map here:
        # st.map([{"lat": float(location["latitude"]), "lon": float(location["longitude"])}])
        
        if not st.session_state['chat_started']:
            if st.button("Continue to Chat"):
                st.session_state['chat_started'] = True
                st.rerun()
    else:
        st.warning("📍 Waiting for location access...")
        st.info(
            """Please ensure:
            1. Location permissions are enabled in your browser.
            2. You've accepted the location prompt."""
        )

with col2:
    if st.button("Reset/Restart"):
        # Reset all session state variables
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Only show chat interface after location is verified and chat is started ---
if st.session_state['location'] and st.session_state['chat_started']:
    # Initialize chat history if empty
    if not st.session_state['history']:
        initial_message = "Hi! I can provide general recommendations or filter by a in-kind partners list if you prefer."
        st.session_state['history'].append({"role": "model", "content": initial_message})
    
    # Display Conversation History
    for turn in st.session_state['history']:
        role = "user" if turn["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(turn["content"])

    # User Input
    user_input = st.chat_input("Enter your message:")

    if user_input:
        # Add user message to history and display it
        st.session_state['history'].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Prepare a placeholder for the assistant's response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Searching for restaurants...▌")

        # Build the full prompt from the system prompt, current location, and conversation history
        prompt_parts = [system_prompt]
        # Always update location
        if location and isinstance(location, dict) and location.get("latitude"):
            st.session_state['location'] = location
        
        prompt_parts.append(
            f"User's current location: Latitude {st.session_state['location']['latitude']}, "
            f"Longitude {st.session_state['location']['longitude']}"
        )
        
        # Append conversation history
        for turn in st.session_state['history']:
            prompt_parts.append(f"{turn['role']}: {turn['content']}")
        
        full_prompt = "\n".join(prompt_parts)

        # Generate and stream the response from the model
        full_response = ""
        try:
            # Use a spinner to indicate waiting for the complete response
            with st.spinner("Waiting for response from LLM..."):
                response = model.generate_content(full_prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        # Update the message placeholder with the streaming content plus a cursor
                        message_placeholder.markdown(full_response + "▌")
                # Once streaming is complete, update without the cursor
                message_placeholder.markdown(full_response)
        except Exception as e:
            message_placeholder.markdown("Sorry, I encountered an error.")
            st.error(f"An error occurred: {e}")
            full_response = "Error: No response received."

        # Add the final model response to the conversation history
        st.session_state['history'].append({"role": "model", "content": full_response})
elif not st.session_state['location']:
    st.warning("⚠️ Please share your location to start chatting")
elif not st.session_state['chat_started']:
    st.info("Click 'Continue to Chat' to begin the conversation")
