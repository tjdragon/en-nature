import decimal
import json
from crewai.tools import BaseTool  # Assuming BaseTool is in crewai.tools
import snowflake.connector

SNOWFLAKE_USER = ''
SNOWFLAKE_PASSWORD = ''
SNOWFLAKE_ACCOUNT = ''
SNOWFLAKE_WAREHOUSE = ''
SNOWFLAKE_DATABASE = ''
# SNOWFLAKE_SCHEMA = os.environ.get("SNOWFLAKE_SCHEMA")  # Optional, but recommended

class CustomerDataTool(BaseTool):
    name:str = "Customer Query Tool"  # No type hint here; it's an instance attribute
    description:str = "Retrieve spending habits and preferences of customers"

    def _run(self, argument: str) -> str:
        print("Running the tool with argument:", argument)
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
                    WHERE U.id = {argument};""")
        results = cur.fetchall()
        columns = [col[0] for col in cur.description]
        json_results = [dict(zip(columns, row)) for row in results]
        def decimal_default(obj):
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            raise TypeError

        json_string = json.dumps(json_results, default=decimal_default)
        return json_string

    # It's good practice to define a separate function for data retrieval
    # (or whatever your tool does)
    # def get_customer_data(self, customer_id):
    #     # Your logic to fetch customer data goes here
    #     # This might involve database queries, API calls, etc.
    #     # Example (replace with your actual implementation):
    #     # if customer_id == "123":
    #     #     return {"name": "John Doe", "spending": 1000}
    #     # else:
    #     #     return {}
    #     raise NotImplementedError("get_customer_data needs to be implemented")


# Example usage (outside the class definition):
tool_instance = CustomerDataTool()  # Create an instance of the tool
result = tool_instance._run("21")  # Call the _run method with an argument
print(result)

# Or, if you're using a Crew AI agent, you would add the tool to the agent:
# from crewai.agents import Agent
# agent = Agent(...) # Initialize your agent
# agent.add_tool(tool_instance) # Add the tool instance to the agent
# agent.run(...) # Use your agent to run with the tool