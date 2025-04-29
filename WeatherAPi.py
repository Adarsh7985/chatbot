import chatbot
import requests
import streamlit as st
import openai
def get_weather(city):
    api_key = "60f4a2c9d19f2183eeafeee3c1060947"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    response = requests.get(url)
    return response.json()

input=st.text_input("Enter City Name")
st.json(get_weather(input))
weather = get_weather(input)
st.header(weather['wind']['speed'])