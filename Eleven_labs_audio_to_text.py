import streamlit as st
from elevenlabs import ElevenLabs
# Streamlit file uploader for audio
uploaded_audio = st.audio_input("Upload an audio file")
if uploaded_audio:
    st.audio(uploaded_audio)
    # Initialize ElevenLabs client (replace with your actual API key)
    client = ElevenLabs(api_key="sk_d916c40f729e95a61c81a09f7c175fb3903b110f430c4bc8")
    # Send to ElevenLabs speech-to-text (example API call)
    response = client.speech_to_text.convert(
        model_id="scribe_v1",
        file={"type": "file", "value": uploaded_audio},
    )
    # Display transcription result
    st.write("### Transcription Result:")
    results = response.json()
    st.json(results)
