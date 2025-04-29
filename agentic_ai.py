# chatbot with the help langgraph + multiple tools
# ReAct => Reasoning and acting
# tools
#=======================================ALL LIBRARY INCLUDED======================================================#
from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper,ArxivAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
import streamlit as st
from langchain_core.runnables import Runnable
from langchain_core.tools import Tool
import pyttsx3
import time
import os
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage, HumanMessage
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
import base64
import requests

#==============================================LOAD API KEY TOOL==========================================================#

#intergrate tools in workflow
load_dotenv()
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
# os.environ["WEATHER_API_KEY"] = os.getenv("WEATHER_API_KEY")

#==========================================LOAN API(OWN)=================================================================#

class LoanAPIWrapper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get_loan_info(self, name: str, field: str = "all") -> str:
        try:
            response = requests.get(f"{self.base_url}/loans/{name}", timeout=10)
            response.raise_for_status()
            data = response.json()

            field = field.lower()

            if field in ["amount", "loan", "loan amount"]:
                loan_amount = data.get("loanAmount")
                if loan_amount is not None:
                    return f"Loan amount for {name} is ₹{loan_amount}"
                else:
                    return f"No loan amount found for {name}"

            elif field in ["interest", "interest rate"]:
                interest = data.get("interestRate")
                if interest is not None:
                    return f"Interest rate for {name} is {interest}%"
                else:
                    return f"No interest rate found for {name}"

            elif field in ["duration", "duration months"]:
                duration = data.get("durationMonths")
                if duration is not None:
                    return f"Loan duration for {name} is {duration} months"
                else:
                    return f"No duration found for {name}"

            else:
                return (
                    f"Loan details for {name}:\n"
                    f" - Amount: ₹{data.get('loanAmount')}\n"
                    f" - Interest Rate: {data.get('interestRate')}%\n"
                    f" - Duration: {data.get('durationMonths')} months"
                )

        except Exception as e:
            return f"API error: {str(e)}"


class LoanQueryRun(Runnable):
    name = "get_loan_info"
    description = "Get loan details for a given customer name."

    def __init__(self, api_wrapper: LoanAPIWrapper):
        self.api_wrapper = api_wrapper

    def invoke(self, input: str, config=None) -> str:
        """
        Accepts input in format: "name" or "name|field"
        Example: "Adarsh" -> full info
                 "Adarsh|amount" -> only loan amount
        """
        if "|" in input:
            name, field = input.split("|", 1)
            return self.api_wrapper.get_loan_info(name.strip(), field.strip())
        else:
            return self.api_wrapper.get_loan_info(input.strip(), "all")


# Set up the API and LangChain Tool
loan_api_url = "http://127.0.0.1:5000"
loan_api_wrapper = LoanAPIWrapper(base_url=loan_api_url)
loan_tool_runnable = LoanQueryRun(api_wrapper=loan_api_wrapper)

loan_tool = Tool(
    name="get_loan",
    description="Fetches loan info. Use: name or name|field (e.g., Adarsh or Adarsh|interest)",
    func=loan_tool_runnable.invoke
)




#==========================================WEATHER API=============================================================#
# own wrapper
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


# own tool ( Creation own api tool )
weather_api_key = os.getenv("WEATHER_API_KEY")  # ← your real API key here
weather_api_wrapper = WeatherAPIWrapper(api_key=weather_api_key)
weather_tool_runnable= WeatherQueryRun(api_wrapper=weather_api_wrapper)
# print(weather_tool_runnable.invoke("Noida"))

weather_tool = Tool(
    name="get_weather",
    description="Get the current weather for a given location.",
    func=weather_tool_runnable.invoke
)



#==============================================ARXIV TOOL==========================================================#
# tool 1
api_wrapper_arxiv=ArxivAPIWrapper(top_k_results=2,doc_content_chars_max=500)
arxiv=ArxivQueryRun(api_wrapper=api_wrapper_arxiv,description="Query arxiv papers")
# print(arxiv.name)
# print(arxiv.invoke("Attention is all you need"))

#==============================================WIKIPEDIA TOOL==========================================================#
# tool 2
api_wrapper_wiki=WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=500)
wiki=WikipediaQueryRun(api_wrapper=api_wrapper_wiki)
#print(wiki.name)



#==============================================TAVILY TOOL==========================================================#
# tool 3
tavily=TavilySearchResults()
# print(tavily.invoke("Provide me the recent ai news?"))


#==============================================CALLING IN TOOL==========================================================#
#combine all tools
tools=[arxiv,wiki,tavily,weather_tool,loan_tool]

#==============================================LLM MODEL TOOL==========================================================#
llm=ChatGroq(model="qwen-qwq-32b")
#print(llm.invoke("What is ai?"))
llm_with_tools=llm.bind_tools(tools=tools)
# excecute
#print(llm_with_tools.invoke("What is the recent news on ai?"))#by using this we easily invoke which api call



#==============================================WORKFLOW TOOL==========================================================#
class State(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]

#==============================================DISPLAY TOOL==========================================================#

from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

def tool_call(state: State):
    return {"messages":[llm_with_tools.invoke(state["messages"])]}

#==============================================ADDING A NODE AND EDGES==========================================================#

builder=StateGraph(State)
builder.add_node("tool_call",tool_call)
builder.add_node("tools",ToolNode(tools))

#edges
builder.add_edge(START,"tool_call")
builder.add_conditional_edges(
    "tool_call",
    tools_condition,
)
# builder.add_edge("tools",END)
builder.add_edge("tools","tool_call") # one call to another
graph=builder.compile()

#==============================================PRINTING THE DATA IN TEXT TOOL==========================================================#
# txt=st.text_input("Enter the information that you want to display")
# messages=graph.invoke({"messages":HumanMessage(content="Hi my name is Charlie please give my loan amount")})
# for i, m in enumerate(messages["messages"]):
#     print(f"\n🔹 Message {i+1}: {m.type}")
#     print(m.content)
# for m in messages["messages"]:
#     m.pretty_print()



#==============================================PARAMETERS/DATA OF TEXT TO SPEECH==========================================================#
#Now Speak something which converts your speech into the txt then pass into msg
# 3de86bed-c61f-4a85-a275-0e8be87cc723
speechurl = "https://api.sarvam.ai/text-to-speech"
headers = {
    "api-subscription-key": os.getenv("SARVAM_API_KEY"),
    "Content-Type": "application/json"
}
#==============PARAMETERS/DATA OF SPEECH TO TEXT===================#
header = {
    'api-subscription-key': os.getenv("SARVAM_API_KEY")
}
txt=""
texturl = "https://api.sarvam.ai/speech-to-text-translate"

#===============================================SPEAK TO UPLOAD YOUR AUDIO=========================================================#
st.header("Chatbot")
uploaded_audio = st.audio_input("Ask Your Query")
if uploaded_audio is not None:
    files = {
        'file': (uploaded_audio.name, uploaded_audio, 'audio/mpeg')
    }
    response = requests.post(texturl, headers=header, files=files)
    # st.subheader(f"Status Code: {response.status_code}")
    # st.text("Response:")
    # st.write(response.text)
    txt=response.json()

#=====================================================ASK=================================================#
    # st.write(txt["transcript"])
# txt = st.text_input("Enter the information that you want to display")
    response = graph.invoke({"messages": HumanMessage(content=txt["transcript"])})
    for i, m in enumerate(response["messages"]):
        if m.type=="tool":
            continue
        else:
            if len(m.content)==0:
                continue
            else:
                # st.markdown(f"### 🔹 Message: {m.type}")
                #speak these m.content
                # st.header(f"Length of message content: {len(m.content)}")
                # st.write(m.content)
                payload = {
                    "speaker": "meera",
                    "pitch": 0,
                    "pace": 1,
                    "loudness": 1,
                    "speech_sample_rate": 22050,
                    "enable_preprocessing": False,
                    "text": m.content,
                    "target_language_code": "en-IN",
                    "model": "bulbul:v1"
                }
                response = requests.request("POST", speechurl, json=payload, headers=headers)
                # Check if the request was successful
                if response.status_code == 200 and m.type=="ai":
                    # If successful, print the response data
                    response_data=response.json()
                    # Decode the Base64 string to binary
                    base64_audio_data = response_data["audios"][0]
                    # Decode the Base64 string to binary
                    audio_data = base64.b64decode(base64_audio_data)
                    # Write the decoded binary data to an MP3 file
                    with open("outputad.mp3", "wb") as audio_file:
                        audio_file.write(audio_data)
                    # print("Audio file has been saved as output_audio.mp3")
                    st.audio("outputad.mp3", format="audio/mpeg", autoplay=True)