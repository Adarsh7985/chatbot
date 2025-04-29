# # 3de86bed-c61f-4a85-a275-0e8be87cc723
# import requests
# import base64
# import streamlit as st
# from playsound import playsound
# import requests
# url = "https://api.sarvam.ai/text-to-speech"
# payload = {
#     "speaker": "meera",
#     "pitch": 0,
#     "pace": 1,
#     "loudness": 1,
#     "speech_sample_rate": 22050,
#     "enable_preprocessing": False,
#     "text": "hello what is your name my name is adarsh",
#     "target_language_code": "en-IN",
#     "model": "bulbul:v1"
# }
# headers = {
#     "api-subscription-key": "3de86bed-c61f-4a85-a275-0e8be87cc723",
#     "Content-Type": "application/json"
# }
# response = requests.request("POST", url, json=payload, headers=headers)
# response_data=response.json()
# base64_audio_data = response_data["audios"][0]
# # Decode the Base64 string to binary
# audio_data = base64.b64decode(base64_audio_data)
# # Write the decoded binary data to an MP3 file
# with open("outputad.mp3", "wb") as audio_file:
#     audio_file.write(audio_data)
# print("Audio file has been saved as output_audio.mp3")
# st.audio("outputad.mp3", format="audio/mpeg", autoplay=True)


#=============================================SPEECH TO TEXT===========================================================#


import requests
import streamlit as st
st.title("Speech to Text Translator")
txt=""
url = "https://api.sarvam.ai/speech-to-text-translate"
uploaded_audio = st.audio_input("Upload a text")
headers = {
    'api-subscription-key': "3de86bed-c61f-4a85-a275-0e8be87cc723"
}
if uploaded_audio is not None:
    files = {
        'file': (uploaded_audio.name, uploaded_audio, 'audio/mpeg')
    }
    response = requests.post(url, headers=headers, files=files)
    st.subheader(f"Status Code: {response.status_code}")
    # st.text("Response:")
    st.write(response.text)
    txt=response.json()
    st.write(txt["transcript"])

# response={"request_id":"20250429_7009fb89-d095-41cc-8148-516892fa6538","transcript":"My name is Alex Chaturvedi, tell me my loan amount.","language_code":"hi-IN"};
# print(response["transcript"])
