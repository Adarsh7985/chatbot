# import requests
# pd=requests.get("http://127.0.0.1:5000/loans")
# data=pd.json()
# print(data)


import requests
import base64
from playsound import playsound
# Your API Key
api_key = "YOUR_API_KEY"  # Replace with your actual API key

# Set the URL for the text-to-speech API with timestamps
url = "https://api.elevenlabs.io/v1/text-to-speech/CwhRBWXzGAHq8TQ4Fs17/with-timestamps"

# Set the headers, including the API key for authorization
headers = {
    "xi-api-key": "sk_d916c40f729e95a61c81a09f7c175fb3903b110f430c4bc8",  # Replace this with your actual API key
}

body = {
    # "text": "इनपुट उपकरण आपके द्वारा चुनी गई भाषा में वेब पर कहीं भी लिखना आसान बनाता है. और जानेंइसे आज़माने के लिए, नीचे अपनी भाषा और इनपुट उपकरण चुनें और लिखना आरंभ करें.",  # The text to convert to speech
    "text":"ಇಂಗ್ಲಿಷ್ ಬಳಸಿ ಕನ್ನಡ (ಕನ್ನಡ ಪ್ರಕಾರ) ಟೈಪ್ ಮಾಡುವುದು ತುಂಬಾ ಸುಲಭ ಮತ್ತು ಸರಳವಾಗಿದೆ. ಕೊಟ್ಟಿರುವ ಪೆಟ್ಟಿಗೆಯಲ್ಲಿ ಪಠ್ಯವನ್ನು ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ ಜಾಗವನ್ನು ಒತ್ತಿ, ಅದು ಪಠ್ಯವನ್ನು ಕನ್ನಡ ಲಿಪಿಗೆ ಪರಿವರ್ತಿಸುತ್ತದೆ.",
    "voice_id": "CwhRBWXzGAHq8TQ4Fs17",  # Voice ID
    "output_format": "mp3_44100_128",  # Optional: specify audio format (e.g., mp3)
    "model_id": "eleven_multilingual_v2"  # Optional: specify model
}
response = requests.post(url, headers=headers, json=body)
print(response)