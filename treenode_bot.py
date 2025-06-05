from typing_extensions import TypedDict
from typing import Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph import StateGraph, END


# --- Define State ---
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_name: Optional[str]
    intent: Optional[str]
    retries: Optional[int]


# --- Node Functions (These must return updated State) ---

# 1. Check if user is known
def check_user_node(state: State) -> State:
    if state.get("user_name"):
        state["messages"].append(HumanMessage(content="Welcome back, what can I help you with?"))
    else:
        state["messages"].append(HumanMessage(content="Hi! What's your name?"))
    return state

# 2. Ask for name and try to extract it
def ask_name(state: State) -> State:
    last_input = state["messages"][-1].content.lower()

    # Attempt to extract the name from the sentence
    if "name is" in last_input:
        name = last_input.split("name is")[-1].strip().split()[0]
        state["user_name"] = name.capitalize()
        state["messages"].append(HumanMessage(content=f"Hello {name}, what can I help you with?"))
    elif "my name is" in last_input:
        name = last_input.split("my name is")[-1].strip().split()[0]
        state["user_name"] = name.capitalize()
        state["messages"].append(HumanMessage(content=f"Hello {name}, what can I help you with?"))
    else:
        state["messages"].append(HumanMessage(content="Please tell me your name using 'my name is ...'"))
    return state

# 3. Process intent (Extract intent)
def process_intent(state: State) -> State:
    last_input = state["messages"][-1].content.lower()

    if "loan" in last_input:
        state["intent"] = "loan"
        state["messages"].append(HumanMessage(content="You want to know your loan amount."))
    elif "weather" in last_input:
        state["intent"] = "weather"
        state["messages"].append(HumanMessage(content="You want to know the weather."))
    else:
        retries = state.get("retries", 0)
        if retries >= 2:
            state["messages"].append(HumanMessage(content="Too many failed attempts. Ending conversation."))
            state["intent"] = "end"
        else:
            state["retries"] = retries + 1
            state["messages"].append(HumanMessage(content="Please say if you want loan info or weather info."))
    return state

# 4. Loan info response
def loan_info(state: State) -> State:
    user = state.get("user_name", "Unknown")
    state["messages"].append(HumanMessage(content=f"Loan info for {user}: ₹1,00,000 @ 7% interest."))
    return state

# 5. Weather info response
def weather_info(state: State) -> State:
    state["messages"].append(HumanMessage(content="The current weather is 28°C and sunny."))
    return state

# 6. End node
def end_node(state: State) -> State:
    state["messages"].append(HumanMessage(content="Thank you! Goodbye!"))
    return state


# --- Routing Functions (Must return the next node name) ---

# Entry point decision
def check_user_router(state: State) -> str:
    return "ask_name" if not state.get("user_name") else "ask_intent"

# Routing after name asking
def ask_name_router(state: State) -> str:
    return "ask_intent" if state.get("user_name") else "ask_name"

# Intent routing
def intent_router(state: State) -> str:
    if state.get("intent") == "loan":
        return "loan_info"
    elif state.get("intent") == "weather":
        return "weather_info"
    elif state.get("intent") == "end" or state.get("retries", 0) >= 2:
        return "end"
    else:
        return "ask_intent"


# --- Build LangGraph ---
builder = StateGraph(State)

# Register all nodes
builder.add_node("check_user", check_user_node)  # node
builder.add_node("ask_name", ask_name)           # node
builder.add_node("ask_intent", process_intent)   # node
builder.add_node("loan_info", loan_info)         # node
builder.add_node("weather_info", weather_info)   # node
builder.add_node("end", end_node)                # node

# Set entry point
builder.set_entry_point("check_user")

# Add routing edges
builder.add_conditional_edges("check_user", check_user_router)
builder.add_conditional_edges("ask_name", ask_name_router)
builder.add_conditional_edges("ask_intent", intent_router)
builder.add_conditional_edges("loan_info", lambda _: "end")
builder.add_conditional_edges("weather_info", lambda _: "end")
builder.add_edge("end", END)

# Compile graph
graph = builder.compile()


# --- Run a Test ---
if __name__ == "__main__":
    state = {
        "messages": [HumanMessage(content="Hi, my name is Adarsh and tell the weather of delhi")],
        "retries": 0
    }

    result = graph.invoke(state)

    print("\n🧾 Final Chatbot Output:")
    for msg in result["messages"]:
        print("→", msg.content)
