from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict
from langchain_groq import ChatGroq
from IPython.display import Image, display
import operator
import os
from dotenv import load_dotenv
from langchain_core.runnables.graph_mermaid import MermaidDrawMethod

# Define the State type
class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

load_dotenv()
# Initialize Groq model (ensure GROQ_API_KEY is set in your environment)
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
model = ChatGroq(model="qwen-qwq-32b")

# Define the node that calls the model
def run_llm(state: State):
    messages = state['messages']
    message = model.invoke(messages)
    return {'messages': [message]}

# Build LangGraph
graph_builder = StateGraph(State)
graph_builder.add_node("llm", run_llm)
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("llm", END)

# Compile the graph (with in-memory checkpointing)
graph = graph_builder.compile(checkpointer=MemorySaver())

# Display the Mermaid diagram of the graph
# display(Image(graph.get_graph().draw_mermaid_png()))
display(Image(graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)))