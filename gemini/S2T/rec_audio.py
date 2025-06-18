import pyaudio
import wave

def record_audio(filename="output.wav", duration=5, rate=44100, channels=1, chunk=1024):
    """Records audio from the microphone and saves it to a WAV file.

    Args:
        filename (str): The name of the output WAV file.
        duration (int): The recording duration in seconds.
        rate (int): The sample rate (samples per second).
        channels (int): The number of audio channels (1 for mono, 2 for stereo).
        chunk (int): The number of frames per buffer.
    """
    try:
        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paInt16,  # 16-bit PCM
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        print(f"Recording for {duration} seconds...")

        frames = []

        for _ in range(0, int(rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)

        print("Finished recording.")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"Audio saved to {filename}")

    except OSError as e:
        print(f"Error: {e}")
        print("Possible causes: Microphone not connected, or already in use by another application. Try closing other applications that might be using your microphone.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    record_audio() #records 5 seconds of audio by default.
    #record_audio(filename="my_recording.wav", duration=10) #example of changing filename and duration.