from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool 

class JSONSearchTool(BaseTool):
    name:str = "json_search"
    description:str = "Search through JSON data to find relevant information"
    data: list = []
    
    def __init__(self, data):
        super().__init__()
        self.data = data
    
    def _run(self, query: str) -> str:
        """Search through JSON data based on query string"""
        results = []
        query = query.lower()
        
        for item in self.data:
            if (query in item['title'].lower() or 
                query in item['content'].lower()):
                results.append(item)
        
        if not results:
            return "No matching documents found."
        
        return str(results)

# Sample JSON data
sample_data = [
    {"id": 1, "title": "Market Analysis Report", "content": "Detailed market analysis..."},
    {"id": 2, "title": "Competitor Research", "content": "Analysis of main competitors..."},
    {"id": 3, "title": "Customer Feedback", "content": "Survey results and feedback..."}
]

# Create JSON Search Tool instance
json_search_tool = JSONSearchTool(data=sample_data)

ikModel = LLM(
    model="ollama/llama3.2:latest",
    # model="ollama/llava-llama3:latest",
    base_url="http://localhost:11434"
)

# Create Agents
researcher = Agent(
    llm=ikModel,
    role='Market Researcher',
    goal='Gather initial market data and trends',
    backstory="""You are an experienced market researcher with expertise 
    in analyzing market trends and gathering relevant data.""",
    verbose=True
)

analyst = Agent(
    llm=ikModel,
    role='Data Analyst',
    goal='Analyze and process market research data',
    backstory="""You are a data analyst specialized in processing and 
    interpreting market research data to extract meaningful insights.""",
    verbose=True
)

report_searcher = Agent(
    llm=ikModel,
    role='Report Searcher',
    goal='Find relevant reports and documents',
    backstory="""You are responsible for finding and retrieving relevant 
    documents and reports from the database.""",
    tools=[json_search_tool],
    verbose=True
)

# Create Tasks
research_task = Task(
    description="""Conduct initial market research and gather relevant data 
    about current market trends.""",
    agent=researcher
)

analysis_task = Task(
    description="""Analyze the gathered market research data and identify 
    key patterns and insights.""",
    agent=analyst
)

search_task = Task(
    description="""Search through existing reports to find relevant 
    information using the provided keywords.""",
    agent=report_searcher
)

# Create and run the crew
crew = Crew(
    agents=[researcher, analyst, report_searcher],
    tasks=[research_task, analysis_task, search_task],
    verbose=True
)

if __name__ == "__main__":
    # Execute the crew's tasks
    result = crew.kickoff()
    print(result)