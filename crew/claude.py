from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool

import decimal
import json
from crewai.tools import BaseTool  # Assuming BaseTool is in crewai.tools
import snowflake.connector

SNOWFLAKE_USER = ''
SNOWFLAKE_PASSWORD = ''
SNOWFLAKE_ACCOUNT = ''
SNOWFLAKE_WAREHOUSE = ''
SNOWFLAKE_DATABASE = ''

class CustomerDataTool(BaseTool):
    name:str = "Customer Query Tool"  # No type hint here; it's an instance attribute
    description:str = "Retrieve spending habits and preferences of customers"

    def _run(self, customer_id: str) -> str:
        print("Running the tool with customer_id:", customer_id)
        # Replace this with your actual tool logic
        # Example:
        # customer_id = argument  # Assuming the argument is a customer ID
        # customer_data = self.get_customer_data(customer_id) # Hypothetical function
        # return str(customer_data) # Convert the result to a string
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
                    WHERE U.id = {customer_id};""")
        results = cur.fetchall()
        columns = [col[0] for col in cur.description]
        json_results = [dict(zip(columns, row)) for row in results]
        def decimal_default(obj):
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            raise TypeError

        json_string = json.dumps(json_results, default=decimal_default)
        print("results", json_string)
        return json_string

ikModel = LLM(
    model="ollama/llama3.2:latest",
    # model="ollama/llava-llama3:latest",
    base_url="http://localhost:11434"
)

def create_customer_agent():
    # Initialize the tool
    #customer_tool = CustomerDataTool()

    # Create an agent with the tool
    agent = Agent(
        role='Customer Data Analyst',
        goal='Analyze customer spending patterns and preferences using the provided tool. Once you gather data just report the average spend of the customer',
        backstory='You are an expert in customer behavior analysis',
        tools=[CustomerDataTool()],
        llm=ikModel,
        allow_delegation=False,
        # max_iter=2,
        verbose=True
    )
    
    return agent

# Example of how to use the agent
def main():
    # Create agent
    customer_agent = create_customer_agent()
    
    # Create task
    customer_task = Task(
        description="Analyze spending patterns for customer id 21",
        expected_output="A detailed analysis of spending patterns including average transaction value and restaurant ids",
        agent=customer_agent
    )
    
    # Create crew
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