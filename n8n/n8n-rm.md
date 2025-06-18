# N8N WorkFlow

Feed the results of the queries for a user and restaurants and ask recommendations.    
The model should describe why it has recommended such and such place.  

Work backward: DB -> Queries -> Data -> LLM

# DB QUERIES

## SQL Queries and Explanations

### Query 1: Detailed Transaction Analysis for a user

```sql
SELECT
    ct.PROJECT_LOCATION_ID,
    pl.PROJECT_ID,
    pl.NAME AS "PROJECT_LOCATION_NAME",
    p.BRAND_ID AS "BRAND ID",
    b.VENUE_STYLE AS "VENUE STYLE",
    bt.NAME AS "BRAND TAG NAME",
    MIN(ct.AMOUNT) AS "MIN AMOUNT",
    MAX(ct.AMOUNT) AS "MAX AMOUNT",
    STDDEV(ct.AMOUNT) AS "STANDARD DEVIATION",
    AVG(ct.AMOUNT) AS "AVERAGE AMOUNT"
FROM
    CREDIT_TRANSACTIONS ct
JOIN
    PROJECT_LOCATIONS pl ON ct.PROJECT_LOCATION_ID = pl.ID
JOIN
    PROJECTS p ON pl.PROJECT_ID = p.ID
JOIN
    BRANDS b ON p.BRAND_ID = b.ID
JOIN
    BRAND_TAGS bt ON b.VENUE_STYLE = bt.ID
WHERE
    ct.USER_ID = 134839
GROUP BY
    ct.PROJECT_LOCATION_ID,
    pl.PROJECT_ID,
    pl.NAME,
    p.BRAND_ID,
    b.VENUE_STYLE,
    bt.NAME;
```
**Explanation:**

This SQL query retrieves the minimum, maximum, standard deviation, and average transaction amounts for a specific user (USER_ID = 134839), along with related project, location, brand, and tag information, grouped by project location and other relevant details.

### Query 2: Transaction Summary by Brand Type
This query summarizes transaction statistics aggregated by the type of brand the user interacted with.

```sql
SELECT
    bt.NAME AS "TYPE",
    ROUND(MIN(ct.AMOUNT)) AS "MIN AMOUNT",
    ROUND(MAX(ct.AMOUNT)) AS "MAX AMOUNT",
    ROUND(STDDEV(ct.AMOUNT)) AS "STANDARD DEVIATION",
    ROUND(AVG(ct.AMOUNT)) AS "AVERAGE AMOUNT",
    COUNT(*) AS "NUMBER OF TIMES USER WENT TO BRAND TYPE"
FROM
    CREDIT_TRANSACTIONS ct
JOIN
    PROJECT_LOCATIONS pl ON ct.PROJECT_LOCATION_ID = pl.ID
JOIN
    PROJECTS p ON pl.PROJECT_ID = p.ID
JOIN
    BRANDS b ON p.BRAND_ID = b.ID
JOIN
    BRAND_TAGS bt ON b.VENUE_STYLE = bt.ID
WHERE
    ct.USER_ID = 134839
GROUP BY
    bt.NAME
ORDER BY
    "TYPE" ASC;
```
**Explanation:**

This SQL query calculates the rounded minimum, maximum, standard deviation, and average transaction amounts, as well as the frequency, for each brand type associated with a specific user (USER_ID = 134839), grouped by brand type and ordered alphabetically.

### Query 2: 
```sql
WITH LocationsNotVisitedByUser AS (
    -- Subquery to find locations in NY not visited by the user
    SELECT
        pl.ID AS LOCATION_ID,
        pl.NAME AS LOCATION_NAME,
        p.NAME AS PROJECT_NAME,
        p.BRAND_ID AS BRAND_ID
    FROM
        PROJECT_LOCATIONS pl
    JOIN
        PROJECTS p ON pl.PROJECT_ID = p.ID
    WHERE
        pl.STATE = 'NY'
        AND pl.ID NOT IN (
            SELECT DISTINCT
                ct.PROJECT_LOCATION_ID
            FROM
                CREDIT_TRANSACTIONS ct
            WHERE
                ct.USER_ID = 134839
        )
)
SELECT
    lnvu.PROJECT_NAME,
    COALESCE(ROUND(MIN(ct.AMOUNT)), 0) AS "MIN AMOUNT",
    COALESCE(ROUND(MAX(ct.AMOUNT)), 0) AS "MAX AMOUNT",
    COALESCE(ROUND(STDDEV(ct.AMOUNT)), 0) AS "STANDARD DEVIATION",
    COALESCE(ROUND(AVG(ct.AMOUNT)), 0) AS "AVERAGE AMOUNT"
FROM
    LocationsNotVisitedByUser lnvu
JOIN
    BRANDS b ON lnvu.BRAND_ID = b.ID
JOIN
    BRAND_TAGS bt ON b.VENUE_STYLE = bt.ID
LEFT JOIN
    CREDIT_TRANSACTIONS ct ON lnvu.LOCATION_ID = ct.PROJECT_LOCATION_ID
WHERE
    bt.NAME = 'Vegetarian'  -- Filter for Vegetarian brand tag
GROUP BY
    lnvu.PROJECT_NAME
ORDER BY
    lnvu.PROJECT_NAME;
```

**Explanation**
1 - Identifies locations in New York state that user 134839 has not visited.
2 - Filters these locations to include only those associated with projects that have the 'Vegetarian' brand tag.
3 - Calculates the rounded minimum, maximum, standard deviation, and average transaction amounts for each of these projects (using LEFT JOIN and COALESCE to handle projects without transactions).
4 - Presents the project name and the calculated aggregate amounts, ordered by project name.
