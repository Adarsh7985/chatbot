from pydub import AudioSegment
import os
import requests
import base64
import streamlit as st
import requests


def show(filename):
    txt=""
    with open(filename, 'rb') as f:
        response = requests.post(
            "https://api.sarvam.ai/speech-to-text",
            headers={
                "api-subscription-key": "3de86bed-c61f-4a85-a275-0e8be87cc723"
            },
            data={
                'model': "saarika:flash",
                'language_code': (None, "hi-IN")
            },
            files={
                'file': (filename, f, 'audio/mpeg')
            },
        )
        resp = response.json()['transcript']
        print(resp)
        return resp


wholetxt=""

def split_audio(input_file,chunk_length_ms=25000):
    # Load the audio file
    global wholetxt
    audio = AudioSegment.from_file(input_file)
    # Calculate the number of chunks
    duration_ms = len(audio)  # Duration in milliseconds
    num_chunks = duration_ms // chunk_length_ms  # How many full chunks of 30 seconds
    # Create output directory if it doesn't exist
    output_dir = "chunks"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Split the audio into chunks
    c=0
    for i in range(num_chunks + 1):
        start_time = i * chunk_length_ms
        end_time = start_time + chunk_length_ms
        chunk = audio[start_time:end_time]
        # Save each chunk as a new file
        if c==4:
            break
        else:
            chunk_filename = f"{output_dir}/chunk_{i + 1}.mp3"
            chunk.export(chunk_filename, format="mp3")
            txt=show(chunk_filename)
            wholetxt=wholetxt+txt+" "
        c=c+1

    print("Audio splitting complete.")

#
#
# Example usage:
input_audio = "9742937821_12571_20250429-090434-all.mp3"  # Path to your audio file
split_audio(input_audio)

# print(wholetxt)
#
# Define the TTS endpoint and headers
speechurl = "https://api.sarvam.ai/text-to-speech"
headers = {
    "api-subscription-key": os.getenv("SARVAM_API_KEY") or "3de86bed-c61f-4a85-a275-0e8be87cc723",
    "Content-Type": "application/json"
}

# Create the payload for TTS request
payload = {
    "speaker": "meera",
    "pitch": 0,
    "pace": 1,
    "loudness": 1,
    "speech_sample_rate": 22050,
    "enable_preprocessing": False,
    "text": wholetxt,
    "target_language_code": "hi-IN",
    "model": "bulbul:v1",

}

# Send the POST request
response = requests.post(speechurl, json=payload, headers=headers)

# Display the raw response
st.write("Raw response:", response)

if response.status_code == 200:
    response_data = response.json()
    st.write("Response JSON:", response_data)

    # Extract and decode audio
    base64_audio_data = response_data["audios"][0]
    audio_data = base64.b64decode(base64_audio_data)

    # Save MP3 to disk
    with open("outputad.mp3", "wb") as audio_file:
        audio_file.write(audio_data)

    # Play audio in Streamlit
    st.audio("outputad.mp3", format="audio/mpeg", autoplay=True)

else:
    st.error(f"Failed with status code: {response.status_code}")
    st.write(response.text)
