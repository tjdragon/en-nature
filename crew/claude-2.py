from crewai import Agent, Task, Crew, LLM
from tools import SnowFlakeSearchTool

ikModel = LLM(
    model="ollama/llama3.2:latest",
    # model="ollama/llava-llama3:latest",
    base_url="http://localhost:11434"
)

def create_customer_agent():
    agent = Agent(
        role='Customer Data Retriever',
        goal='Retrieve customer data and pass it to the next agent for analysis',
        backstory='You are an expert in customer data retrieval',
        tools=[SnowFlakeSearchTool()],
        llm=ikModel,
        allow_delegation=False,
        # max_iter=2,
        verbose=True
    )
    
    return agent


def main():
    customer_agent = create_customer_agent()
    
    customer_task = Task(
        description="Retrieve data for customer id 21",
        expected_output="An analysis of the spending habits of given customer using JSON query search",
        agent=customer_agent
    )

    crew = Crew(
        agents=[customer_agent],
        tasks=[customer_task],
        verbose=True
    )
    
    # Run the analysis
    result = crew.kickoff()
    print(result)

if __name__ == "__main__":
    main()