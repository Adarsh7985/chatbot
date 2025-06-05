from zep_cloud.client import Zep
from zep_cloud import Message
import rich
import uuid
from typing import List, Dict, Optional
from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langchain_core.tools import Tool
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
import requests




ZEP_API_KEY = 'z_1dWlkIjoiYzA4YWEzNmEtODNmYy00NTVhLThiM2ItZWVhY2IzMmRlMGUzIn0.xS7raWicwY7X49PnIc73Lvm7-gRiJgWi2rfKTUWoc3rXS9DniWDlK6f_az3TtK7GSAB2HF8mqizjwVR6R7jt_g'
client = Zep(
    api_key=ZEP_API_KEY,
)

load_dotenv()
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

bot_name = "SupportBot"

user_name = "James"
user_id = user_name + str(uuid.uuid4())[:4]
session_id = str(uuid.uuid4())

client.user.add(
    user_id=user_id,
    email=f"{user_name}@abcd.com",
    first_name=user_name,
    last_name="J",
)

client.memory.add_session(
    user_id=user_id,
    session_id=session_id,
)

chat_history = [
    {
        "role": "assistant",
        "name": bot_name,
        "content": f"Hello {user_name}, welcome to QuickEats support. How can I assist you today?",
        "timestamp": "2024-11-01T12:00:00Z",
    },
    {
        "role": "user",
        "name": user_name,
        "content": "This is unbelievable! My food was supposed to arrive an hour ago!",
        "timestamp": "2024-11-01T12:01:00Z",
    },
    {
        "role": "assistant",
        "name": bot_name,
        "content": f"I'm really sorry to hear about the delay, {user_name}. I understand how frustrating it is to wait longer than expected for your meal. Could you share your order details with me so I can look into this right away?",
        "timestamp": "2024-11-01T12:02:00Z",
    },
    {
        "role": "user",
        "name": user_name,
        "content": "I ordered at 11:00 AM, and it said it would be here by 11:30! Now it's 12:01, and still nothing!",
        "timestamp": "2024-11-01T12:03:00Z",
    },
    {
        "role": "assistant",
        "name": bot_name,
        "content": f"I apologize for the inconvenience, {user_name}. This delay is certainly not up to our standards. Let me check with the restaurant and delivery partner to get an update on your order status. I'll update you as soon as I have more information.",
        "timestamp": "2024-11-01T12:04:00Z",
    },
    {
        "role": "user",
        "name": user_name,
        "content": "This is really unacceptable. I'm starving here, and there's no communication from your side!",
        "timestamp": "2024-11-01T12:05:00Z",
    },
    {
        "role": "assistant",
        "name": bot_name,
        "content": f"I completely understand, {user_name}, and I apologize for the lack of updates. We're committed to making this right. I'll escalate your order as a priority, and in the meantime, I'll also apply a discount to your account as a gesture of apology.",
        "timestamp": "2024-11-01T12:06:00Z",
    },
]





def convert_to_zep_messages(chat_history: List[Dict[str, Optional[str]]]) -> List[Message]:

    return [
        Message(
            role_type=msg["role"],
            role=msg.get("name", None),
            content=msg["content"],
        )
        for msg in chat_history
    ]

formatted_chat_messages = convert_to_zep_messages(chat_history)

client.memory.add(
    session_id=session_id, messages= formatted_chat_messages
)


fact_response = client.user.get_facts(user_id=user_id)
for fact in fact_response.facts:
    rich.print(fact)
session_facts = client.memory.get(session_id=session_id)
rich.print([r.fact for r in session_facts.relevant_facts])


class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_name: str
    session_id: str



async def search_facts(state: State, query: str, limit: int = 5):
    """Search for facts in all conversations had with a user.

    Args:
        state (State): The Agent's state.
        query (str): The search query.
        limit (int): The number of results to return. Defaults to 5.

    Returns:
        list: A list of facts that match the search query.
    """
    return await client.memory.search_sessions(user_id=state['user_name'], text=query, limit=limit,
                                               search_scope="facts")


tools = [search_facts]
model=ChatGroq(model="qwen-qwq-32b")
llm_with_tools=model.bind_tools(tools=tools)

def trim_messages(messages, max_tokens=3):
    return messages[-max_tokens:]

def chatbot(state: State):
    memory = client.memory.get(state["session_id"])
    facts_string = ""
    if memory.relevant_facts:
        facts_string = "\n".join([f.fact for f in memory.relevant_facts])

    system_message = SystemMessage(
        content=f"""You are a knowledgeable and empathetic assistant,
        here to help users with various queries including weather information.
        Review the information about the user and their prior conversation history below to provide accurate, thoughtful, and personalized advice.
        Facts about the user and their conversation:
        {facts_string or 'No facts about the user and their conversation'}"""
    )

    messages = [system_message] + state["messages"]

    # Invoke weather tool when the query is related to weather
    response = model.invoke(messages)

    # Add the new chat turn to the Zep graph
    messages_to_save = [
        Message(
            role_type="user",
            role=state["user_name"],
            content=state["messages"][-1].content,
        ),
        Message(role_type="assistant", content=response.content),
    ]

    client.memory.add(
        session_id=state["session_id"],
        messages=messages_to_save,
    )

    # Truncate the chat history to keep the state from growing unbounded.
    state["messages"] = trim_messages(state["messages"], max_tokens=3)
    return {"messages": [response]}

graph_builder = StateGraph(State)

memory = MemorySaver()

def should_continue(state, config):
    messages = state['messages']
    last_message = messages[-1]
    # If there is no function call, then we finish.
    if not last_message.tool_calls:
        return 'end'
    # Otherwise if there is, we continue.
    else:
        return 'continue'

tools = [search_facts]
model = ChatGroq(model="qwen-qwq-32b")
llm_with_tools = model.bind_tools(tools=tools)




graph_builder.add_node('agent', chatbot)
graph_builder.add_node('tools', ToolNode(tools))  # ✅ FIXED HERE


graph_builder.add_node('weather_tool', ToolNode([]))
graph_builder.add_edge(START, 'agent')
graph_builder.add_conditional_edges('agent', should_continue, {'continue': 'tools', 'end': END})
graph_builder.add_edge('tools', 'agent')


graph = graph_builder.compile(checkpointer=memory)
# display(Image(graph.get_graph().draw_mermaid_png()))

def extract_messages(result):
    output = ""
    for message in result['messages']:
        if isinstance(message, AIMessage):
            role = "assistant"
        else:
            role = result['user_name']
        output += f"{role}: {message.content}\n"
    return output.strip()

def graph_invoke(message: str, user_name: str, thread_id: str, ai_response_only: bool = True):
    r = graph.invoke(
        {
            'messages': [
                {
                    'role': 'user',
                    'content': message,
                }
            ],
            'user_name': user_name,
            'session_id': thread_id,
        },
        config={'configurable': {'thread_id': thread_id}},
    )

    if ai_response_only:
        return r['messages'][-1].content
    else:
        return extract_messages(r)

user_name = 'James_' + uuid.uuid4().hex[:4]
session_id = uuid.uuid4().hex

client.user.add(user_id=user_name)
client.memory.add_session(session_id=session_id,
                          user_id=user_name)

while True:

    user_input = input("Enter your message (type 'quit' to exit): ")

    if user_input.lower() == "quit":
        print("Exiting...")
        break

    # Call the graph_invoke function with user input
    r = graph_invoke(
        user_input,  # The message from the user
        user_name,  # Provide the user name variable
        session_id,  # Provide the session ID variable
    )

    # Print the response from graph_invoke
    print("Response:", r)

session_facts = client.memory.get(session_id=session_id)
rich.print([r.fact for r in session_facts.relevant_facts])


# # chatbot with the help langgraph + multiple tools
# # ReAct => Reasoning and acting
# # tools
# #=======================================ALL LIBRARY INCLUDED======================================================#
# from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun
# from langchain_community.utilities import WikipediaAPIWrapper,ArxivAPIWrapper
# from langchain_community.tools.tavily_search import TavilySearchResults
# import streamlit as st
# from langchain_core.runnables import Runnable
# from langchain_core.tools import Tool
# import pyttsx3
# import time
# import os
# from dotenv import load_dotenv
# from typing_extensions import TypedDict
# from langchain_core.messages import AnyMessage, HumanMessage
# from typing import Annotated
# from langgraph.graph.message import add_messages
# from langchain_groq import ChatGroq
# import base64
# import requests
#
# #==============================================LOAD API KEY TOOL==========================================================#
#
# #intergrate tools in workflow
# load_dotenv()
# os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
# # os.environ["WEATHER_API_KEY"] = os.getenv("WEATHER_API_KEY")
#
# #==========================================LOAN API(OWN)=================================================================#
#
# class LoanAPIWrapper:
#     def __init__(self, base_url: str):
#         self.base_url = base_url.rstrip("/")
#
#     def get_loan_info(self, name: str, field: str = "all") -> str:
#         try:
#             response = requests.get(f"{self.base_url}/loans/{name}", timeout=10)
#             response.raise_for_status()
#             data = response.json()
#
#             field = field.lower()
#
#             if field in ["amount", "loan", "loan amount"]:
#                 loan_amount = data.get("loanAmount")
#                 if loan_amount is not None:
#                     return f"Loan amount for {name} is ₹{loan_amount}"
#                 else:
#                     return f"No loan amount found for {name}"
#
#             elif field in ["interest", "interest rate"]:
#                 interest = data.get("interestRate")
#                 if interest is not None:
#                     return f"Interest rate for {name} is {interest}%"
#                 else:
#                     return f"No interest rate found for {name}"
#
#             elif field in ["duration", "duration months"]:
#                 duration = data.get("durationMonths")
#                 if duration is not None:
#                     return f"Loan duration for {name} is {duration} months"
#                 else:
#                     return f"No duration found for {name}"
#
#             else:
#                 return (
#                     f"Loan details for {name}:\n"
#                     f" - Amount: ₹{data.get('loanAmount')}\n"
#                     f" - Interest Rate: {data.get('interestRate')}%\n"
#                     f" - Duration: {data.get('durationMonths')} months"
#                 )
#
#         except Exception as e:
#             return f"API error: {str(e)}"
#
#
# class LoanQueryRun(Runnable):
#     name = "get_loan_info"
#     description = "Get loan details for a given customer name."
#
#     def __init__(self, api_wrapper: LoanAPIWrapper):
#         self.api_wrapper = api_wrapper
#
#     def invoke(self, input: str, config=None) -> str:
#         """
#         Accepts input in format: "name" or "name|field"
#         Example: "Adarsh" -> full info
#                  "Adarsh|amount" -> only loan amount
#         """
#         if "|" in input:
#             name, field = input.split("|", 1)
#             return self.api_wrapper.get_loan_info(name.strip(), field.strip())
#         else:
#             return self.api_wrapper.get_loan_info(input.strip(), "all")
#
#
# # Set up the API and LangChain Tool
# loan_api_url = "http://127.0.0.1:5000"
# loan_api_wrapper = LoanAPIWrapper(base_url=loan_api_url)
# loan_tool_runnable = LoanQueryRun(api_wrapper=loan_api_wrapper)
#
# loan_tool = Tool(
#     name="get_loan",
#     description="Fetches loan info. Use: name or name|field (e.g., Adarsh or Adarsh|interest)",
#     func=loan_tool_runnable.invoke
# )
#
# # weather_tool_runnable.invoke("Noida")
#
#
# #==========================================WEATHER API=============================================================#
# # own wrapper
# class WeatherAPIWrapper:
#     def __init__(self, api_key: str):
#         self.api_key = api_key
#         self.base_url = "https://api.openweathermap.org/data/2.5/weather"
#
#     def run(self, location: str) -> str:
#         try:
#             params = {
#                 "q": location,
#                 "units": "metric",
#                 "appid": self.api_key
#             }
#             response = requests.get(self.base_url, params=params, timeout=10)
#             response.raise_for_status()
#             data = response.json()
#             weather = data["weather"][0]["description"]
#             temp = data["main"]["temp"]
#             return f"The weather in {location} is {weather} with temperature {temp}°C"
#         except Exception as e:
#             return f"API error: {str(e)}"
#
# # ⚙️ 2. LangChain Runnable Wrapper
# class WeatherQueryRun(Runnable):
#     name = "get_weather"
#     description = "Get the current weather for a given location."
#
#     def __init__(self, api_wrapper: WeatherAPIWrapper):
#         self.api_wrapper = api_wrapper
#
#     def invoke(self, input: str, config=None) -> str:
#         return self.api_wrapper.run(input)
#
#
# # own tool ( Creation own api tool )
# weather_api_key = os.getenv("WEATHER_API_KEY")  # ← your real API key here
# weather_api_wrapper = WeatherAPIWrapper(api_key=weather_api_key)
# weather_tool_runnable= WeatherQueryRun(api_wrapper=weather_api_wrapper)
# # print(weather_tool_runnable.invoke("Noida"))
#
# weather_tool = Tool(
#     name="get_weather",
#     description="Get the current weather for a given location.",
#     func=weather_tool_runnable.invoke
# )
#
#
#
# #==============================================ARXIV TOOL==========================================================#
# # tool 1
# api_wrapper_arxiv=ArxivAPIWrapper(top_k_results=2,doc_content_chars_max=500)
# arxiv=ArxivQueryRun(api_wrapper=api_wrapper_arxiv,description="Query arxiv papers")
# # print(arxiv.name)
# # print(arxiv.invoke("Attention is all you need"))
#
# #==============================================WIKIPEDIA TOOL==========================================================#
# # tool 2
# api_wrapper_wiki=WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=500)
# wiki=WikipediaQueryRun(api_wrapper=api_wrapper_wiki)
# #print(wiki.name)
#
#
#
# #==============================================TAVILY TOOL==========================================================#
# # tool 3
# tavily=TavilySearchResults()
# # print(tavily.invoke("Provide me the recent ai news?"))
#
#
# #==============================================CALLING IN TOOL==========================================================#
# #combine all tools
# tools=[arxiv,wiki,tavily,weather_tool,loan_tool]
#
# #==============================================LLM MODEL TOOL==========================================================#
# llm=ChatGroq(model="qwen-qwq-32b")
# #print(llm.invoke("What is ai?"))
# llm_with_tools=llm.bind_tools(tools=tools)
# # excecute
# #print(llm_with_tools.invoke("What is the recent news on ai?"))#by using this we easily invoke which api call
#
#
#
# #==============================================WORKFLOW TOOL==========================================================#
# class State(TypedDict):
#     messages:Annotated[list[AnyMessage],add_messages]
#
# #==============================================DISPLAY TOOL(TOOL CALL)==========================================================#
#
# from IPython.display import Image, display
# from langgraph.graph import StateGraph, START, END
# from langgraph.prebuilt import ToolNode
# from langgraph.prebuilt import tools_condition
#
# def tool_call(state: State):
#     return {"messages":[llm_with_tools.invoke(state["messages"])]}
#
# #==============================================ADDING A NODE AND EDGES==========================================================#
#
# builder=StateGraph(State)
# builder.add_node("tool_call",tool_call)
# builder.add_node("tools",ToolNode(tools))
#
# #edges
# builder.add_edge(START,"tool_call")
# builder.add_conditional_edges(
#     "tool_call",
#     tools_condition,
# )
# # builder.add_edge("tools",END)
# builder.add_edge("tools","tool_call") # one call to another, for more than one sentence
# builder.compile(checkpointer=memory)
#
#
# #==============================================PRINTING THE DATA IN TEXT TOOL==========================================================#
# # txt=st.text_input("Enter the information that you want to display")
# messages=graph.invoke({"messages":HumanMessage(content="Hi my name is Charlie please give my loan amount")})
# for i, m in enumerate(messages["messages"]):
#     print(f"\n🔹 Message {i+1}: {m.type}")
#     print(m.content)
# for m in messages["messages"]:
#     m.pretty_print()
