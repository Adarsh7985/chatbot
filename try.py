import streamlit as st
import requests
import google.generativeai as genai

# --- Configure Gemini API ---
GOOGLE_API_KEY = "AIzaSyApBDE6H-tTJfAeKri42JYeqXWFSGIipTg"
genai.configure(api_key=GOOGLE_API_KEY)

# --- OpenWeatherMap API ---
def get_weather(city):
    api_key = "60f4a2c9d19f2183eeafeee3c1060947"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    return requests.get(url).json()

# --- Extract City from Query using Gemini ---
# def extract_city(query):
#     model = genai.GenerativeModel("models/gemini-1.5-flash")
#     prompt = f"Extract only the city name from this weather-related query: '{query}'. Return only the city name."
#     return model.generate_content(prompt).text.strip()

def extract_city(query):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    prompt = (
        f"Your task is to extract the city name from this user query: '{query}'. "
        f"Only return the name of a real, known city if the query is clean and contains no irrelevant or extra words. "
        f"If the query contains any unrelated or confusing words (e.g., 'bottle', 'apple', 'chair', etc.), "
        f"respond strictly with: No city found. Do not explain or add anything else."
    )
    response = model.generate_content(prompt).text.strip()

    # Normalize response
    if response.lower() == "no city found":
        return None
    return response




# --- Extract Weather Detail from Query using Gemini ---
def extract_detail_type(query):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    prompt = f"What weather detail is the user asking for in this query: '{query}'? Reply with one word: 'temperature', 'humidity', 'wind', or 'general'."
    return model.generate_content(prompt).text.strip().lower()

# --- Use Gemini for general city questions ---
def ask_gemini_about_city(city, user_query):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    prompt = f"The user wants to know this about the city {city}: '{user_query}'. Respond in a helpful, friendly way."
    return model.generate_content(prompt).text.strip()

# --- Streamlit App Setup ---
st.set_page_config(page_title="🌤️ Weather Query Bot")
st.header("🌦️ Weather Query Bot")

# --- Session State Initialization ---
if 'city' not in st.session_state:
    st.session_state.city = None
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'weather_shown' not in st.session_state:
    st.session_state.weather_shown = False

# --- Step 1: Initial Weather Query ---
user_input = st.text_input("Ask about the weather (e.g., 'What's the temperature in Delhi?'):")

if st.button("Ask Weather") and user_input:
    city = extract_city(user_input)
    detail = extract_detail_type(user_input)
    st.session_state.city = city

    if city:
        st.write(f"📍 City: **{city}**")
        st.write(f"🔍 Detail asked: **{detail}**")

        weather = get_weather(city)
        if weather.get('cod') == 200:
            st.session_state.weather_data = weather
            temp = weather['main']['temp']
            feels_like = weather['main']['feels_like']
            description = weather['weather'][0]['description']
            humidity = weather['main']['humidity']
            wind = weather['wind']['speed']

            if detail == "temperature":
                st.success(f"The temperature in {city} is {temp}°C. Feels like {feels_like}°C.")
            elif detail == "humidity":
                st.success(f"The humidity in {city} is {humidity}%.")
            elif detail == "wind":
                st.success(f"The wind speed in {city} is {wind} m/s.")
            else:
                st.success(
                    f"It’s currently {temp}°C with {description} in {city}. "
                    f"Feels like {feels_like}°C, humidity is {humidity}%, wind speed is {wind} m/s."
                )

            st.session_state.weather_shown = True
        else:
            st.error("❌ Couldn't fetch weather. Try a different city.")
    else:
        st.warning("⚠️ City could not be identified.")

# --- Step 2: Loop for Follow-Up Questions ---
if st.session_state.weather_shown:
    st.subheader(f"🤔 Want to ask more about **{st.session_state.city}**?")
    with st.form("follow_up_form"):
        follow_up = st.text_input("Ask something else (e.g., 'What's the humidity?', 'Tell me more about the climate'):")
        ask = st.form_submit_button("Ask")

    if ask and follow_up:
        detail = extract_detail_type(follow_up)
        weather = st.session_state.weather_data
        city = st.session_state.city
        temp = weather['main']['temp']
        feels_like = weather['main']['feels_like']
        description = weather['weather'][0]['description']
        humidity = weather['main']['humidity']
        wind = weather['wind']['speed']

        if detail == "temperature":
            st.info(f"The temperature in {city} is {temp}°C. Feels like {feels_like}°C.")
        elif detail == "humidity":
            st.info(f"The humidity in {city} is {humidity}%.")
        elif detail == "wind":
            st.info(f"The wind speed in {city} is {wind} m/s.")
        else:
            response = ask_gemini_about_city(city, follow_up)
            st.info("Sorry We provided only weather information.")
