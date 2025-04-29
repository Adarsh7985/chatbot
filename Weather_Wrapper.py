import requests
from langchain_core.runnables import Runnable
from langchain_core.tools import Tool

# 🌤️ 1. API Wrapper Class
class WeatherAPIWrapper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def run(self, location: str) -> str:
        try:
            params = {
                "q": location,
                "units": "metric",
                "appid": self.api_key
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            return f"The weather in {location} is {weather} with temperature {temp}°C"
        except Exception as e:
            return f"API error: {str(e)}"

# ⚙️ 2. LangChain Runnable Wrapper
class WeatherQueryRun(Runnable):
    name = "get_weather"
    description = "Get the current weather for a given location."

    def __init__(self, api_wrapper: WeatherAPIWrapper):
        self.api_wrapper = api_wrapper

    def invoke(self, input: str, config=None) -> str:
        return self.api_wrapper.run(input)

# 🔌 3. Instantiate Everything
weather_api_key = "60f4a2c9d19f2183eeafeee3c1060947"  # ← your real API key here
api_wrapper = WeatherAPIWrapper(api_key=weather_api_key)
weather_tool_runnable = WeatherQueryRun(api_wrapper=api_wrapper)

# ✅ Test it
print(weather_tool_runnable.invoke("Noida"))
print(weather_tool_runnable.invoke("bangalore"))

# 🧠 4. Make a LangChain Tool (for agent or LangGraph)
weather_tool = Tool(
    name="weather",
    description="Get current weather for a city",
    func=weather_tool_runnable.invoke
)