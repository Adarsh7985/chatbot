import chatbot
import requests
import openai
from openai import OpenAI
# Set your API keys
# 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
weather_api_key = "60f4a2c9d19f2183eeafeee3c1060947"

client = OpenAI(api_key="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")  # Replace with your actual API key

# 🌤️ Function to fetch weather data from OpenWeatherMap
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={weather_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        return f"The weather in {city} is {description} with {temp}°C (feels like {feels_like}°C) and {humidity}% humidity."
    else:
        return "Sorry, I couldn’t retrieve the weather for that city."


# 🧠 Main function that talks to GPT and uses the tool
def ask_gpt_about_weather(prompt):
    # Let GPT know it has access to a tool called "get_weather"
    system_prompt = """
You are a smart assistant who can check real-time weather.
You can use the get_weather(city) function to find the current weather.
Extract the city from the user's message and use the tool.
Then give a natural, friendly weather update.
"""

    # Step 1: Use GPT to extract the city
    extract_city_prompt = f"From this prompt: \"{prompt}\", what is the city mentioned?"

    city_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": extract_city_prompt}
        ]
    )

    city = city_response['choices'][0]['message']['content'].strip().replace(".", "")
    print(f"📍 Extracted City: {city}")

    # Step 2: Call weather function
    weather_report = get_weather(city)

    # Step 3: Ask GPT to write a friendly reply using the report
    final_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",
             "content": f"Here’s the weather data for {city}: {weather_report}. Please reply naturally."}
        ]
    )

    return final_response['choices'][0]['message']['content'].strip()


# 🏁 Run it
user_prompt = "What's the weather like in Mumbai today?"
response = ask_gpt_about_weather(user_prompt)
print("\n🤖 GPT Response:", response)
