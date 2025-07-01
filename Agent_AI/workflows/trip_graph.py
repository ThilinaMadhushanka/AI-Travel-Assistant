from langgraph.graph import StateGraph
from agents.planner import run_planner
from agents.budgeter import run_budgeter
from agents.booking import run_booking
from typing import TypedDict, Annotated

# Define the state schema
class TripState(TypedDict):
    input: str
    planner_output: str | None
    budgeter_output: str | None
    booking_output: str | None

# Create state graph with schema
builder = StateGraph(state_schema=TripState)

# Add nodes with state updates
def planner_node(state: TripState):
    state["planner_output"] = run_planner(state["input"])
    return state

def budgeter_node(state: TripState):
    state["budgeter_output"] = run_budgeter(state["planner_output"])
    return state

def booking_node(state: TripState):
    state["booking_output"] = run_booking(state["budgeter_output"])
    return state

builder.add_node("Planner", planner_node)
builder.add_node("Budgeter", budgeter_node)
builder.add_node("Booking", booking_node)

builder.add_edge("Planner", "Budgeter")
builder.add_edge("Budgeter", "Booking")

builder.set_entry_point("Planner")
graph = builder.compile()

def plan_trip(input_data: dict):
    initial_state = {"input": input_data["input"], 
                    "planner_output": None,
                    "budgeter_output": None,
                    "booking_output": None}
    result = graph.invoke(initial_state)
    return result
