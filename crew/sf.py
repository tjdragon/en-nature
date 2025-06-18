import snowflake.connector

# Snowflake credentials (best practice: use environment variables)
SNOWFLAKE_USER = ''
SNOWFLAKE_PASSWORD = ''
SNOWFLAKE_ACCOUNT = ''
SNOWFLAKE_WAREHOUSE = ''
SNOWFLAKE_DATABASE = ''
# SNOWFLAKE_SCHEMA = os.environ.get("SNOWFLAKE_SCHEMA")  # Optional, but recommended

conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE
)

print("Connected to Snowflake!", conn)