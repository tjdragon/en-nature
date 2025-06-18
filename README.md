# IK

## Concept

- SQL Queries will be used as a tool for IK
- The project will use a Customer Id as an input and its (optional) current geo-location
- The user will be guided through the process to avoid direct conversation with the LLM which might lead to hallucination and/or misinformation like a ChatBot

### Example (*)
- Bot: Let me help you today. Are you looking for a recommendation based on where you usually go (1) or where you are right now (2) or at a different location (3)
- This will allow us to generate sql queries and filter out data (the fewer the data the better for a LLM), effectively imposing constraints

#### Queries for a given user

- Q1: Find the min, max, avg spend of a user group by restaurant id (project location)
- Join with Restaurant id, location, food type, rating and if the user liked it
- -> This gives User X spends Y on avg at Place Z that serves A and he liked/disliked it

#### Queries for restaurants
- Q2: Using the constraints (*), find the restaurants, food type, average spend, rating, etc. and
- group with all users who have been to those

At this stage we have enough info to feed the LLM

## Queries for LLMS

### Customer
Find the min, max, avg spend of a user group by restaurant id.  
Join with Restaurant id, location, food type, rating and if the user liked it.  
This gives User X spends Y on avg at Place Z that serves A and he liked/disliked it.

- TODO

### Restaurants
Using the constraints:

- Where the customer is right now
- Where the customer usually goes
- Different location

 find the restaurants, food type, average spend, rating, etc. and group with all users who have been to those

 - TODO

 ## Sample queries

 ### Returns users and amounts at different restaurant ids
 ```sql
 SELECT
    u.ID,
    ct.AMOUNT,
    ct.PROJECT_LOCATION_ID,
    MIN(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS min_amount,
    MAX(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS max_amount,
    STDDEV(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS stddev_amount,
    AVG(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS average_amount,
FROM
    IK_PRODUCTION."USERS" u
JOIN
    IK_PRODUCTION.CREDIT_TRANSACTIONS ct ON u.ID = ct.USER_ID;
 ```

 ### Same as before for NYK Users
 ```sql
 SELECT
    u.ID,
    ct.AMOUNT,
    ct.PROJECT_LOCATION_ID,
    MIN(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS min_amount,
    MAX(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS max_amount,
    STDDEV(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS stddev_amount,
    AVG(ct.AMOUNT) OVER (PARTITION BY ct.USER_ID) AS average_amount,
FROM
    IK_PRODUCTION."USERS" u
JOIN
    IK_PRODUCTION.CREDIT_TRANSACTIONS ct ON u.ID = ct.USER_ID
JOIN 
	IK_PRODUCTION.COORDINATE_CITIES cc ON u.PRIMARY_CITY_ID = cc.ID
WHERE 
	cc.CITY = 'New York';
 ```

 ### Restaurants Data
 ```sql
     plpd.PROJECT_LOCATION_ID,
    plpd."NAME",
    plpd.TYPES,
    plpd.RATING,
    AVG(ct.AMOUNT) AS average_amount
FROM
    IK_PRODUCTION.PROJECT_LOCATIONS_PLACES_DATA plpd
JOIN
    IK_PRODUCTION.CREDIT_TRANSACTIONS ct ON plpd.PROJECT_LOCATION_ID = ct.PROJECT_LOCATION_ID
GROUP BY
    plpd.PROJECT_LOCATION_ID,
    plpd."NAME",
    plpd.TYPES,
    plpd.RATING
ORDER BY
    plpd.PROJECT_LOCATION_ID ;
 ```

 ### Restaurant Types
 ```sql
 SELECT 
--	p.ID  AS PROJECT_ID,
--	p.BRAND_ID,
	pl.ID AS PROJECT_LOC_ID,
--	btb.BRAND_TAG_ID,
	bt.SLUG 
FROM 
	IK_PRODUCTION.PROJECTS p 
JOIN
	IK_PRODUCTION.PROJECT_LOCATIONS pl ON p.ID = pl.PROJECT_ID
JOIN 
	IK_PRODUCTION.BRAND_TAGS_BRANDS btb ON btb.BRAND_ID = p.BRAND_ID
JOIN 
	IK_PRODUCTION.BRAND_TAGS bt ON bt.ID = btb.BRAND_TAG_ID;
 ```

 ### Favorite Restaurant
 ```sql
 SELECT
    UB.USER_ID,
--    UB.BRAND_ID,
    pl.ID AS PROJECT_LOCATION_ID,
    UB.IS_FAVORITE,
--	p.ID AS PROJECT_ID
FROM
	IK_PRODUCTION.USER_BRANDS ub
JOIN
	IK_PRODUCTION.PROJECTS p ON P.BRAND_ID = UB.BRAND_ID
JOIN
	IK_PRODUCTION.PROJECT_LOCATIONS pl ON pl.PROJECT_ID = p.ID
WHERE
	PL.CITY = 'New York'
 ```

 ## Misc
 ### How-To Auto-Ident
 ```cmd
  python  -m autopep8 --in-place .\claude-3.py
 ```