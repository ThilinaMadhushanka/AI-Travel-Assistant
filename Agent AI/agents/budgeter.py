from crewai import Agent, Task, Crew

def run_budgeter(input_text):
    budgeter = Agent(
        name="BudgetManager",
        role="Financial Advisor",
        goal="Allocate a trip budget efficiently for transport, stay, and food.",
        tools=[],
        backstory="You are a finance-savvy assistant optimizing travel costs."
    )
    
    budget_task = Task(
        description=f"Create a budget plan based on: {input_text}",
        expected_output="A detailed budget breakdown including transportation, accommodation, food, and activities costs.",
        agent=budgeter
    )
    
    crew = Crew(
        agents=[budgeter],
        tasks=[budget_task]
    )
    
    return crew.kickoff()