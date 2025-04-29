# import pyttsx3
# text_speech=pyttsx3.init()
# ans=input("Text")
# text_speech.say(ans)
# text_speech.runAndWait()
# import elevenlabs
#
# audio = elevenlabs.generate(
#     text="hello my name is adarsh",
#     voice="Bella"
# )
#
# elevenlabs.play(audio)




# from elevenlabs import ElevenLabs
# client = ElevenLabs(
#     api_key="sk_d916c40f729e95a61c81a09f7c175fb3903b110f430c4bc8",
# )
# client.text_to_speech.convert_with_timestamps(
#     voice_id="21m00Tcm4TlvDq8ikWAM",
#     text="This is a test for the API of ElevenLabs.",
# )
# from elevenlabs import ElevenLabs
#
# # Create the client with your API key
# client = ElevenLabs(api_key="sk_d916c40f729e95a61c81a09f7c175fb3903b110f430c4bc829e95a61c81a09f7c175fb3903b110f430c4bc8")
#
# # Generate audio
# audio = client.text_to_speech.generate(
#     text="Hello, my name is Adarsh.",
#     voice="Bella"
# )
# client.text_to_speech.play(audio)



from elevenlabs import ElevenLabs

client = ElevenLabs(api_key="api", )
audio=client.text_to_speech.convert(
	voice_id="JBFqnCBsd6RMkjVDRZzb",
	output_format="mp3_44100_128",
	text="The first move is what sets everything in motion.",
	model_id="eleven_multilingual_v2"
)
with open("output.mp3", "wb") as f:
    f.write(audio)

# https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb?output_format=mp3_44100_128