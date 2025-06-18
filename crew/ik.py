from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

########################
# LLM MODEL DEFINITION #
########################
ikModel = LLM(
    model="ollama/llama3.2:latest",
    base_url="http://localhost:11434"
)

#############################
# CUSTOMER AGENT DEFINITION #
#############################

class CustomerDataTool(BaseTool):
    name: str = "Customer Query Tool"
    description: str = "Retrieve spending habits and preferences of customers"

    def _run(self, argument: str) -> str:
        print("Running the tool with argument:", argument)
        return "Tool's result"

customer_agent = Agent(
    role="Customer Data Agent",
    goal="Retrieve spending habits and preferences of customers",
    backstory="You are gathering data about a customer and the restaurants they visited and the amount they spent",
    llm=ikModel,
    tools=[CustomerDataTool()],
    verbose=True,
    allow_delegation=False
)

customer_task = Task(
    description="Query the customer data",
    agent=customer_agent,
)

crew = Crew(
    agents=[customer_agent],
    tasks=[customer_task],
    verbose=True,
    process=Process.sequential,
)

print("Crew Kickoff")
result = crew.kickoff()
print(result)