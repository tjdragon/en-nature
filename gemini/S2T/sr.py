import speech_recognition as sr

def audio_to_text(audio_file_path):
    """
    Converts audio from a local file to text.

    Args:
        audio_file_path (str): The path to the audio file.

    Returns:
        str: The transcribed text, or None if an error occurred.
    """
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)  # Record the entire audio file

            # Try Google Web Speech API
            try:
                text = recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                print("Google Web Speech API could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results from Google Web Speech API; {e}")
                return None

    except FileNotFoundError:
        print(f"Error: Audio file not found at {audio_file_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# Example usage:
audio_file = "../audio_uploads/ramen-geneva.wav"  # Replace with your audio file path
transcribed_text = audio_to_text(audio_file)

if transcribed_text:
    print(f"Transcribed Text: {transcribed_text}")

# Example using a different audio file type (.flac):
# audio_file_flac = "path/to/your/audio_file.flac"
# transcribed_text_flac = audio_to_text(audio_file_flac)

# if transcribed_text_flac:
#     print(f"Transcribed Text (FLAC): {transcribed_text_flac}")

# # Example using a different audio file type (.mp3), which may require ffmpeg:
# audio_file_mp3 = "path/to/your/audio_file.mp3"
# transcribed_text_mp3 = audio_to_text(audio_file_mp3)

# if transcribed_text_mp3:
#     print(f"Transcribed Text (MP3): {transcribed_text_mp3}")