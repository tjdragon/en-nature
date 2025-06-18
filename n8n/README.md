# N8N WorkFlow
Feed the results of the queries for a user and restaurants and ask recommendations.
The model should describe why it has recommended such and such place.

Work backward: DB -> Queries -> Data -> LLM

<img width="1429" alt="image" src="https://github.com/user-attachments/assets/362d27e6-9a29-4ec3-a0f5-1c5e950e465f" />

## 1 - QUERY to esablish User Profile

The query analyzes a user's transactions, determines their spending patterns for different cuisine types, and then presents this information in a structured JSON format. This JSON output can be easily used by other applications or systems, including AI agents, for further analysis or to generate recommendations.

```sql
SELECT
  -- Construct the final JSON output
  OBJECT_CONSTRUCT(
    'summary', -- Create a top-level JSON object with the key 'summary'
    ARRAY_AGG( -- Aggregate the JSON objects for each cuisine type into a JSON array
      OBJECT_CONSTRUCT( -- Create a JSON object for each cuisine type
        'Cuisine type', bt."TYPE",  -- Add the cuisine type with the key 'Cuisine type'
        'minium amount spent', "MIN AMOUNT",  -- Add the minimum amount spent with the key 'minium amount spent'
        'maximum amount spent', "MAX AMOUNT",  -- Add the maximum amount spent with the key 'maximum amount spent'
        'standard deviation', "STANDARD DEVIATION"::INTEGER,  -- Add the standard deviation, cast to integer, with the key 'standard deviation'
        'average amount spent', "AVERAGE AMOUNT",  -- Add the average amount spent with the key 'average amount spent'
        'Number of times the user went to this Cuisine type', "NUMBER OF TIMES USER WENT TO BRAND TYPE"  -- Add the count of visits with the key 'Number of times the user went to this Cuisine type'
      )
    )
  ) AS json_output  -- Alias the final JSON output as 'json_output'
FROM
  (
    -- Subquery to calculate statistics for each cuisine type
    SELECT
      bt.NAME AS "TYPE",  -- Select the brand tag name and alias it as "TYPE"
      ROUND(MIN(ct.AMOUNT)) AS "MIN AMOUNT",  -- Calculate the rounded minimum transaction amount and alias it as "MIN AMOUNT"
      ROUND(MAX(ct.AMOUNT)) AS "MAX AMOUNT",  -- Calculate the rounded maximum transaction amount and alias it as "MAX AMOUNT"
      ROUND(STDDEV(ct.AMOUNT)) AS "STANDARD DEVIATION",  -- Calculate the rounded standard deviation of transaction amounts and alias it as "STANDARD DEVIATION"
      ROUND(AVG(ct.AMOUNT)) AS "AVERAGE AMOUNT",  -- Calculate the rounded average transaction amount and alias it as "AVERAGE AMOUNT"
      COUNT(*) AS "NUMBER OF TIMES USER WENT TO BRAND TYPE"  -- Count the number of transactions for each brand type and alias it as "NUMBER OF TIMES USER WENT TO BRAND TYPE"
    FROM
      CREDIT_TRANSACTIONS ct  -- Select from the CREDIT_TRANSACTIONS table (aliased as ct)
      JOIN PROJECT_LOCATIONS pl ON ct.PROJECT_LOCATION_ID = pl.ID  -- Join with PROJECT_LOCATIONS (aliased as pl) on PROJECT_LOCATION_ID
      JOIN PROJECTS p ON pl.PROJECT_ID = p.ID  -- Join with PROJECTS (aliased as p) on PROJECT_ID
      JOIN BRANDS b ON p.BRAND_ID = b.ID  -- Join with BRANDS (aliased as b) on BRAND_ID
      JOIN BRAND_TAGS bt ON b.VENUE_STYLE = bt.ID  -- Join with BRAND_TAGS (aliased as bt) on VENUE_STYLE
    WHERE
      ct.USER_ID = :USER_ID  -- Filter transactions for a specific user (:USER_ID is a placeholder for the user ID)
    GROUP BY
      bt.NAME  -- Group the results by brand tag name ("TYPE")
    ORDER BY
      "TYPE" ASC  -- Order the results by "TYPE" in ascending order
  ) bt;
```
**EXAMPLE OUTPUT**
```json
{
  "summary": [
    {
      "Cuisine type": "Vegan",
      "Number of times the user went to this Cuisine type": 9,
      "average amount spent": 84,
      "maximum amount spent": 249,
      "minium amount spent": 12,
      "standard deviation": 93
    },
    {
      "Cuisine type": "Vegetarian",
      "Number of times the user went to this Cuisine type": 34,
      "average amount spent": 74,
      "maximum amount spent": 425,
      "minium amount spent": 1,
      "standard deviation": 107
    },
    {
      "Cuisine type": "Healthy",
      "Number of times the user went to this Cuisine type": 37,
      "average amount spent": 121,
      "maximum amount spent": 428,
      "minium amount spent": 9,
      "standard deviation": 79
    },
    {
      "Cuisine type": "American Fare",
      "Number of times the user went to this Cuisine type": 2,
      "average amount spent": 41,
      "maximum amount spent": 63,
      "minium amount spent": 18,
      "standard deviation": 32
    },
    {
      "Cuisine type": "Farm To Table",
      "Number of times the user went to this Cuisine type": 16,
      "average amount spent": 1,
      "maximum amount spent": 1,
      "minium amount spent": 1,
      "standard deviation": 0
    }
  ]
}
```



## 2 - QUERY to esablish User Profile
The query identifies projects of specified cuisine types (for example : 'Healthy' and 'Vegan') in New York ( NY )  that a particular user hasn't visited. It then calculates aggregate spending statistics for these projects and returns the data as a JSON array, where each element represents a project with its associated spending information. This JSON can be used by a recommendation system to suggest relevant projects to the user.

```sql
WITH LocationsNotVisitedByUser AS (
    -- Subquery to find locations in NY not visited by a specific user
    SELECT
        pl.ID AS LOCATION_ID,
        pl.NAME AS LOCATION_NAME,
        p.NAME AS PROJECT_NAME,
        p.BRAND_ID AS BRAND_ID
    FROM
        PROJECT_LOCATIONS pl  -- Select from the PROJECT_LOCATIONS table (alias pl)
    JOIN
        PROJECTS p ON pl.PROJECT_ID = p.ID  -- Join with the PROJECTS table (alias p) using PROJECT_ID
    WHERE
        pl.STATE = 'NY'  -- Filter for locations in New York state
        AND pl.ID NOT IN (
            SELECT DISTINCT
                ct.PROJECT_LOCATION_ID
            FROM
                CREDIT_TRANSACTIONS ct
            WHERE
                ct.USER_ID = {{ $json.user_id }}  -- Exclude locations visited by the user specified by the input parameter $json.user_id
        )
),
ProjectAggregation AS (
    -- Aggregate data for each project not visited by the user
    SELECT
        lnvu.PROJECT_NAME,  -- Select the project name
        OBJECT_CONSTRUCT(  -- Construct a JSON object for each project
            'project_name', lnvu.PROJECT_NAME,  -- Project name as a key-value pair
            'min_amount', COALESCE(ROUND(MIN(ct.AMOUNT)), 0),  -- Minimum transaction amount, rounded and coalesced to 0 if NULL
            'max_amount', COALESCE(ROUND(MAX(ct.AMOUNT)), 0),  -- Maximum transaction amount, rounded and coalesced to 0 if NULL
            'standard_deviation', COALESCE(ROUND(STDDEV(ct.AMOUNT)), 0)::INTEGER,  -- Standard deviation of transaction amounts, rounded, cast to integer, and coalesced to 0 if NULL
            'average_amount', COALESCE(ROUND(AVG(ct.AMOUNT)), 0)  -- Average transaction amount, rounded and coalesced to 0 if NULL
        ) AS project_json  -- Alias the constructed JSON object as 'project_json'
    FROM
        LocationsNotVisitedByUser lnvu  -- Select from the CTE (locations not visited by the user)
    JOIN
        BRANDS b ON lnvu.BRAND_ID = b.ID  -- Join with the BRANDS table using BRAND_ID
    JOIN
        BRAND_TAGS bt ON b.VENUE_STYLE = bt.ID  -- Join with the BRAND_TAGS table using VENUE_STYLE
    LEFT JOIN
        CREDIT_TRANSACTIONS ct ON lnvu.LOCATION_ID = ct.PROJECT_LOCATION_ID  -- Left join with CREDIT_TRANSACTIONS to get transaction amounts
    WHERE
        bt.NAME IN ('{{ $json.recomended_cuisine_type[0] }}', '{{ $json.recomended_cuisine_type[1] }}')  -- Filter for specific brand tag names (cuisine types) provided as input parameters
    GROUP BY
        lnvu.PROJECT_NAME  -- Group results by project name
)
SELECT
    ARRAY_AGG(project_json) AS potential_projects  -- Aggregate the project JSON objects into a single JSON array and alias it as 'potential_projects'
FROM
    ProjectAggregation;  -- Select from the ProjectAggregation CTE
```

**EXAMPLE OUTPUT**
```json
[
  {
    "project_name": "Project Beta",
    "min_amount": 25,
    "max_amount": 50,
    "standard_deviation": 18,
    "average_amount": 38
  },
  {
    "project_name": "Project Gamma",
    "min_amount": 0,
    "max_amount": 0,
    "standard_deviation": 0,
    "average_amount": 0
  }
]
```

## AI AGENT 1 ( User Profiling Agent ) 
The AI agent, acting as a User Profiling Agent, will analyze a user's spending data (provided as a JSON object) to create a profile and recommend **two cuisine types**. 
It will determine the user's preferred brand types based on spending amounts and visit frequency, then choose **two cuisine types** from a predefined list that best align with these preferences. 
The agent will output a JSON object containing : 
* the user ID, the recommended cuisine types
* a rationale for each recommendation
* an estimated potential average spending.

The agent's analysis will focus on identifying the user's spending habits, inferring their preferences, and making data-driven recommendations within the specified JSON format, also will take into consideration the user's ID, the spending patterns and the brand type preferences provided in the input data.

## AI AGENT 2 ( Recommendation Agent )
**For the sake of the example, we are going to filter on NY projects**

This AI agent, acting as a Recommendation Agent, will analyze project data (provided in JSON format), and recommend four projects to a user. The recommendations will be based on : 
* the user's ID
* their preferred cuisine types ( Example : "Healthy" and "Vegan")
* their expected average spending of ( Example : $100 )
<img width="507" alt="image" src="https://github.com/user-attachments/assets/4fd32a49-1121-4ca5-a2d7-4cf22c52390b" />


The agent will prioritize projects with an average spending amount close to ( Example : $100 ) (+/- $20 or a reasonable range based on the data), potentially considering the consistency of spending (standard deviation) if the data is available. 

The agent will then output the **four project recommendations** in a specific plain text format, including a project name and a clear rationale based on the data for each recommendation, this format will be used by a downstream agent in an n8n workflow.
<img width="781" alt="image" src="https://github.com/user-attachments/assets/a4f6773c-1aad-43c2-82e2-1722a882e22b" />



