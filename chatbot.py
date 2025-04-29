import streamlit as st
import requests
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyApBDE6H-tTJfAeKri42JYeqXWFSGIipTg"

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Function to get weather data
def get_weather(city):
    api_key = "60f4a2c9d19f2183eeafeee3c1060947"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    response = requests.get(url)
    return response.json()

# Updated: Extract only city name using Gemini
def get_city_from_gemini(query):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    chat = model.start_chat(history=[])

    prompt = f"Extract only the city name from this weather-related query: '{query}'. Return only the city name, no explanation."
    response = chat.send_message(prompt)
    return response.text.strip()

# Streamlit UI
st.set_page_config(page_title="Weather Query Bot")
st.header("Weather Bot")

user_input = st.text_input("Ask about the weather (e.g., 'What's the weather like in New York today?'):")

if user_input:
    # Extract city from user input
    city = get_city_from_gemini(user_input)

    if city:
        st.write(f" City identified: **{city}**")

        # Fetch weather
        weather_data = get_weather(city)

        if weather_data.get('cod') == 200:
            temperature = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            description = weather_data['weather'][0]['description']
            humidity = weather_data['main']['humidity']
            wind=weather_data['wind']['speed']

            response = f"It’s currently {temperature}°C with {description} in {city}. It feels like {feels_like}°C with {humidity}% humidity and wind speed is {wind}☀️💧"
            st.success(response)
        else:
            st.error("Couldn't fetch the weather. Please try a different city.")
    else:
        st.warning("Couldn't extract a city from your query. Try rephrasing it.")
