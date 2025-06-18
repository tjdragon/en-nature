from crewai import Agent, LLM, Task
from langchain.tools import Tool

def analyze_json(json_data: str) -> str:
    prompt = f"""
    Analyze this JSON data and provide a concise summary:
    {json_data}
    Include:
    1. Main data structure type
    2. Key fields present
    3. Number of records (if applicable)
    4. Notable patterns or values
    """
    return prompt

def create_json_summarizer():
    ikModel = LLM(
        model="ollama/llama3.2:latest",
        base_url="http://localhost:11434"
    )
    
    json_tool = Tool(
        name='analyze_json',
        func=analyze_json,
        description='Analyzes JSON data and creates a summary'
    )
    
    return Agent(
        role='Data Analyst',
        goal='Analyze and summarize JSON data accurately',
        backstory='Expert at analyzing data structures and creating concise summaries',
        llm=ikModel,
        tools=[json_tool]
    )

if __name__ == "__main__":
    sample_json = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"}
        ]
    }
    
    agent = create_json_summarizer()
     
    task = Task(
        description=f"Summarize this JSON: {sample_json}",
        expected_output="A concise summary of the JSON data structure and contents",
        agent=agent
    )
    result = agent.execute_task(task)
    print(result)