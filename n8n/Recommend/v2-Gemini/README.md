
No more tools ..

Gemini takes 1 million in context,  so i passed the whole list of restaurants that were updated in feb ---->  1296 restaurants

```sql
WITH FilteredLocations AS (
    -- Filter PROJECT_LOCATIONS based on the specified criteria.
    SELECT
        DISTINCT REGEXP_REPLACE(
            p.NAME,
            '\\s*-\\s*.+$',  -- Corrected and simplified regex
            ''  -- Replace with an empty string
        ) AS project_name
    FROM
        IK_PRODUCTION.PROJECT_LOCATIONS pl
    JOIN
        IK_PRODUCTION.PROJECTS p ON pl.PROJECT_ID = p.ID
    JOIN
        IK_PRODUCTION.BRANDS b ON p.BRAND_ID = b.ID
    JOIN
        IK_PRODUCTION.BRAND_TAGS bt ON b.VENUE_STYLE = bt.ID
    WHERE
        pl.UPDATED_AT > '2025-02-01 00:00:16.000'
        AND pl.STATE IS NOT NULL AND pl.STATE <> ''
        AND pl.CITY IS NOT NULL AND pl.CITY <> ''
        AND pl.ZIP_CODE IS NOT NULL AND pl.ZIP_CODE <> ''
        AND pl.NAME IS NOT NULL AND pl.NAME <> ''
        AND pl.LATITUDE IS NOT NULL AND pl.LONGITUDE IS NOT NULL
        AND pl.DELETED_AT IS NULL
        AND b.ID IS NOT NULL
)
-- Final SELECT: Create a JSON array of the cleaned restaurant names.
SELECT
	ARRAY_AGG(project_name) AS restaurant_names
FROM
    FilteredLocations
    ORDER BY restaurant_names ASC;
```
