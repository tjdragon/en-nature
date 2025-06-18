WITH UserProfile AS (
    -- This CTE calculates the user's spending profile and overall average spend.
    SELECT
      ARRAY_AGG(  -- Aggregates the per-cuisine spending details into a JSON array.
          OBJECT_CONSTRUCT(  -- Creates a JSON object for each cuisine type.
            'Cuisine type', "TYPE",  -- Key: 'Cuisine type', Value: Cuisine name.
            'Minimum amount spent', "MIN AMOUNT",  -- Key: 'Minimum amount spent', Value: Minimum spend.
            'Maximum amount spent', "MAX AMOUNT",  -- Key: 'Maximum amount spent', Value: Maximum spend.
            'Standard deviation', "STANDARD DEVIATION",  -- Key: 'Standard deviation', Value: Standard deviation of spend.
            'Average amount spent', "AVERAGE AMOUNT",  -- Key: 'Average amount spent', Value: Average spend.
            'Number of times the user went', "NUMBER OF TIMES USER WENT TO BRAND TYPE"  -- Key: 'Number of times the user went', Value: Visit count.
          )
      ) AS user_profile_array,  -- The resulting JSON array representing the user's profile.
      user_average_spend  -- The user's overall average spend.
    FROM
      (
        -- Inner subquery to calculate per-cuisine statistics and retrieve the pre-calculated overall average.
        SELECT
          bt.NAME AS "TYPE",  -- Cuisine type name.
          ROUND(MIN(ct.AMOUNT)) AS "MIN AMOUNT",  -- Rounded minimum transaction amount for this cuisine.
          ROUND(MAX(ct.AMOUNT)) AS "MAX AMOUNT",  -- Rounded maximum transaction amount for this cuisine.
          ROUND(STDDEV(ct.AMOUNT))::INTEGER AS "STANDARD DEVIATION",  -- Rounded standard deviation of transaction amounts.
          ROUND(AVG(ct.AMOUNT)) AS "AVERAGE AMOUNT",  -- Rounded average transaction amount for this cuisine.
          COUNT(*) AS "NUMBER OF TIMES USER WENT TO BRAND TYPE",  -- Number of transactions for this cuisine type.
          sub.user_average_spend  -- The user's overall average spend (calculated in a separate subquery).
        FROM
          CREDIT_TRANSACTIONS ct  -- Transaction data.
          JOIN PROJECT_LOCATIONS pl ON ct.PROJECT_LOCATION_ID = pl.ID  -- Join with project locations to get location information.
          JOIN PROJECTS p ON pl.PROJECT_ID = p.ID  -- Join with projects to get project information.
          JOIN BRANDS b ON p.BRAND_ID = b.ID  -- Join with brands to link to cuisine types.
          JOIN BRAND_TAGS bt ON b.VENUE_STYLE = bt.ID  -- Join with brand tags to get the cuisine type (e.g., "Italian", "Vegan").
          ,(SELECT ROUND(AVG(amount)) AS user_average_spend FROM CREDIT_TRANSACTIONS WHERE USER_ID = :USER_INTAKE) sub -- Subquery to calculate the overral average spent.
        WHERE
          ct.USER_ID = :USER_INTAKE  -- Filter transactions for the specific user (using a bind variable).
        GROUP BY
          bt.NAME, sub.user_average_spend  -- Group by cuisine type and user average to calculate aggregate statistics per cuisine.
      )
    GROUP BY user_average_spend -- Necessary grouping for the outer aggregation.
),
LocationsNotVisitedByUser AS (
    -- This CTE finds all locations that the user has *not* visited
    -- and that are within 800 meters of the specified coordinates.
   SELECT
        pl.ID AS LOCATION_ID,  -- Unique ID of the location.
        pl.NAME AS LOCATION_NAME,  -- Name of the location (e.g., restaurant name).
        p.NAME AS PROJECT_NAME, -- Name of the project
        p.BRAND_ID AS BRAND_ID,  -- Brand the location belongs to.
        pl.LATITUDE,  -- Latitude coordinate of the location.
        pl.LONGITUDE,  -- Longitude coordinate of the location.
        ST_DISTANCE(  -- Calculate the distance in meters between the user's specified location and each project location.
            ST_MAKEPOINT(:INPUT_LONGITUDE, :INPUT_LATITUDE),  -- User's location (provided as bind variables).
            ST_MAKEPOINT(pl.LONGITUDE, pl.LATITUDE)  -- Project location's coordinates.
        ) AS distance_meters,  -- The calculated distance in meters.
        bt.NAME as BRAND_TAG_NAME  -- The cuisine type associated with the location.
    FROM
        PROJECT_LOCATIONS pl  -- Table containing project location information.
    JOIN
        PROJECTS p ON pl.PROJECT_ID = p.ID  -- Join with the PROJECTS table.
    JOIN
        BRANDS b ON p.BRAND_ID = b.ID  -- Join with the BRANDS table.
    JOIN
        BRAND_TAGS bt ON b.VENUE_STYLE = bt.ID  -- Join with the BRAND_TAGS table.
    WHERE
        pl.ID NOT IN (  -- Filter out locations where the user has existing transactions.
            SELECT DISTINCT
                ct.PROJECT_LOCATION_ID  -- Select distinct location IDs.
            FROM
                CREDIT_TRANSACTIONS ct  -- From the CREDIT_TRANSACTIONS table.
            WHERE
                ct.USER_ID = :USER_INTAKE  -- For the specified user.
                AND ct.PROJECT_LOCATION_ID IS NOT NULL  -- And where the location ID is not NULL.
        )
    AND ST_DISTANCE(  -- Further filter locations to be within 800 meters of the user's specified location.
        ST_MAKEPOINT(:INPUT_LONGITUDE, :INPUT_LATITUDE),
        ST_MAKEPOINT(pl.LONGITUDE, pl.LATITUDE)
    ) <= 800
     AND pl.LATITUDE IS NOT NULL AND pl.LONGITUDE IS NOT NULL  -- Ensure that locations have valid coordinates.
),
Recommendations AS (
    -- This CTE generates the restaurant recommendations.  It filters, ranks, and formats the data.
    SELECT
        ARRAY_AGG(  -- Aggregate the recommendation details for each restaurant into a JSON array.
            OBJECT_CONSTRUCT(  -- Create a JSON object for each recommended restaurant.
                'Restaurant', LOCATION_NAME,  -- Key: 'Restaurant', Value: Restaurant name.
                'Cuisine type', BRAND_TAG_NAME,  -- Key: 'Cuisine type', Value: Cuisine type.
                'Minimum Spend', min_spend,  -- Key: 'Minimum Spend', Value: Minimum spend at the restaurant.
                'Maximum Spend', max_spend,  -- Key: 'Maximum Spend', Value: Maximum spend at the restaurant.
                'Standard Deviation', standard_deviation,  -- Key: 'Standard Deviation', Value: Standard deviation of spend.
                'Average Spend', average_spend,  -- Key: 'Average Spend', Value: Average spend at the restaurant.
                'Distance (meters)', distance_meters::INTEGER  -- Key: 'Distance (meters)', Value: Distance from user, cast to integer.
            )
        ) AS recommendations_array  -- The resulting JSON array of restaurant recommendations.

    FROM
    (
      SELECT
          lnvu.LOCATION_NAME,  -- Restaurant name.
          lnvu.BRAND_TAG_NAME,  -- Cuisine type.
          COALESCE(ROUND(MIN(ct.AMOUNT)), 0) as min_spend,  -- Rounded minimum spend, defaulting to 0 if no transactions.
          COALESCE(ROUND(MAX(ct.AMOUNT)), 0) as max_spend,  -- Rounded maximum spend, defaulting to 0.
          COALESCE(ROUND(STDDEV(ct.AMOUNT)), 0)::INTEGER as standard_deviation,  -- Rounded standard deviation, defaulting to 0.
          COALESCE(ROUND(AVG(ct.AMOUNT)), 0) as average_spend,  -- Rounded average spend, defaulting to 0.
          lnvu.distance_meters,  -- Distance from the user's location.
        ABS(COALESCE(ROUND(AVG(ct.AMOUNT)), 0) - up.user_average_spend) AS diff_from_user_avg,  -- Absolute difference between restaurant average and user's overall average.
        ROW_NUMBER() OVER (ORDER BY ABS(COALESCE(ROUND(AVG(ct.AMOUNT)), 0) - up.user_average_spend) ASC, lnvu.distance_meters ASC) AS rn  -- Rank by difference, then distance.
      FROM
        LocationsNotVisitedByUser lnvu  -- Get locations the user hasn't visited.
      INNER JOIN
        CREDIT_TRANSACTIONS ct ON lnvu.LOCATION_ID = ct.PROJECT_LOCATION_ID  -- INNER JOIN: Only consider locations *with* transactions.
      CROSS JOIN
        UserProfile up  -- CROSS JOIN with UserProfile to get the user's overall average spend (up.user_average_spend).
      GROUP BY  -- Group by location, cuisine, distance, and user's average spend (required for aggregation).
        lnvu.LOCATION_NAME,
        lnvu.BRAND_TAG_NAME,
        lnvu.distance_meters,
        up.user_average_spend
     QUALIFY rn <= 20  -- Keep only the top 20 closest restaurants (based on average spend difference and distance).
    )
)
-- Final SELECT: Combine the results from the CTEs into a single JSON object.
SELECT
    OBJECT_CONSTRUCT(  -- Construct the final JSON object.
        'User id', :USER_INTAKE,  -- Key: 'User id', Value: The user ID (from the bind variable).
        'User profile', up.user_profile_array,  -- Key: 'User profile', Value: The user's profile data (JSON array).
        'User recommendation on the below list of restaurants', r.recommendations_array  -- Key: 'User recommendation...', Value: The recommendations (JSON array).
    ) AS data  -- Alias the final JSON object as 'data'.
FROM UserProfile up, Recommendations r;  -- Combine results from the UserProfile and Recommendations CTEs (effectively a CROSS JOIN, as each returns one row).
