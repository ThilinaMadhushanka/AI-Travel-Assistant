from crewai import Agent, Task, Crew

def run_planner(input_text):
    planner = Agent(
        name="TripPlanner",
        role="Travel Planning Expert",
        goal="Create a detailed day-by-day itinerary for a destination.",
        tools=[],
        backstory="You are an expert travel planner with global destination knowledge."
    )
    
    planning_task = Task(
        description=f"Create a travel plan based on: {input_text}",
        expected_output="A detailed day-by-day travel itinerary including activities, locations, and timing.",
        agent=planner
    )
    
    crew = Crew(
        agents=[planner],
        tasks=[planning_task]
    )
    
    return crew.kickoff()