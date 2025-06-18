from crewai.tools import BaseTool 
import snowflake.connector
import decimal

SNOWFLAKE_USER = ''
SNOWFLAKE_PASSWORD = ''
SNOWFLAKE_ACCOUNT = ''
SNOWFLAKE_WAREHOUSE = ''
SNOWFLAKE_DATABASE = ''

class SnowFlakeSearchTool(BaseTool):
    name:str = "json_search"
    description:str = "Search through JSON data to find relevant information"
    data: list = []
    
    def __init__(self):
        super().__init__()
        print("Running the tool with customer_id 21")

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
        json_results = [dict(zip(columns, row)) for row in results]
        
        self.data = json_results
        print("results", self.data)
    
    def _run(self, query: str) -> str:
        print("Search through JSON data based on query string")
        results = []
        query = query.lower()
        
        for item in self.data:
            if (query in item['CUSTOMER_ID'].lower() or 
                query in item['RESTAURANT_ID'].lower() or
                query in item['AMOUNT_SPENT'].lower() or 
                query in item['MIN_AMOUNT_SPENT'].lower() or 
                query in item['MAX_AMOUNT_SPENT'].lower() or 
                query in item['STDDEV_AMOUNT_SPENT'].lower() or 
                query in item['AVERAGE_AMOUNT_SPENT'].lower()):
                results.append(item)
        
        if not results:
            return "No matching documents found."
        
        return str(results)
    

snst = SnowFlakeSearchTool()