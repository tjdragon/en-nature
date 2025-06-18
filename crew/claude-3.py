from crewai import Agent, LLM, Task
from langchain.tools import Tool
import snowflake.connector

SNOWFLAKE_USER = ''
SNOWFLAKE_PASSWORD = ''
SNOWFLAKE_ACCOUNT = ''
SNOWFLAKE_WAREHOUSE = ''
SNOWFLAKE_DATABASE = ''

def analyze_json(json_data: str) -> str:
    prompt = f"""
    Analyze this JSON data and provide a concise summary:
    {json_data}
    Include:
    1. Spending habits and preferences
    2. Most spent amount at which restaurants ids
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
        backstory='Expert at analyzing customer spending habits and preferences',
        llm=ikModel,
        tools=[json_tool]
    )


if __name__ == "__main__":
    print("Getting data from Snowflake for user 21")
    sf_connection = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE
    )
    cur = sf_connection.cursor()
    cur.execute(f""" 
                    SELECT u.ID AS CUSTOMER_ID,
                    ct.AMOUNT AS AMOUNT_SPENT,
                    ct.PROJECT_LOCATION_ID AS RESTAURANT_ID,
                    MIN(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS MIN_AMOUNT_SPENT,
                    MAX(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS MAX_AMOUNT_SPENT,
                    STDDEV(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS STDDEV_AMOUNT_SPENT,
                    AVG(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS AVERAGE_AMOUNT_SPENT,
                    FROM IK_PRODUCTION."USERS" u
                    JOIN
                    IK_PRODUCTION.CREDIT_TRANSACTIONS ct ON u.ID = ct.USER_ID
                    WHERE U.id = 21;""")
    results = cur.fetchall()
    columns = [col[0] for col in cur.description]
    json_data = [dict(zip(columns, row)) for row in results]
    print("json_data", json_data)

    print("Creating a JSON summarizer agent")
    agent = create_json_summarizer()

    task = Task(
        description=f"Summarize this JSON: {json_data}",
        expected_output="A concise summary of the customer spending habits and preferences",
        agent=agent
    )
    print("Executing task with the agent")
    result = agent.execute_task(task)
    print(result)
