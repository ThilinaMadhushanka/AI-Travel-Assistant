from crewai import Agent, Task, Crew

def run_booking(input_text):
    booking = Agent(
        name="BookingAgent",
        role="Travel Booking Specialist",
        goal="Suggest affordable flights and hotel bookings.",
        tools=[],
        backstory="You specialize in finding best travel deals."
    )
    
    booking_task = Task(
        description=f"Find travel bookings based on: {input_text}",
        expected_output="A list of recommended flights and accommodations with prices and booking details.",
        agent=booking
    )
    
    crew = Crew(
        agents=[booking],
        tasks=[booking_task]
    )
    
    return crew.kickoff()