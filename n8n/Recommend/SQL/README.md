# Restaurant Recommendation Query - Snowflake SQL

This document explains the SQL query designed to generate personalized restaurant recommendations for a user based on their past spending history and a specified location.

## Overview

The query takes a user ID, a latitude, and a longitude as input (via bind variables) and produces a JSON object containing:

1.  **User Profile:** A summary of the user's spending habits, broken down by cuisine type.  This includes the minimum, maximum, average, and standard deviation of their spending, as well as the number of times they've visited restaurants of each cuisine.
2.  **Recommendations:** A list of up to 20 restaurants that the user has *not* visited, within 800 meters of the specified location.  The recommendations are prioritized based on how closely the restaurant's average spending matches the user's *overall* average spending, and then by distance (closer restaurants are preferred).

## Data Model

The query assumes the following database tables and relationships:

*   **`CREDIT_TRANSACTIONS`:** Contains records of user transactions, including:
    *   `USER_ID` (INTEGER):  The ID of the user who made the transaction.
    *   `PROJECT_LOCATION_ID` (INTEGER):  Foreign key referencing `PROJECT_LOCATIONS.ID`.
    *   `AMOUNT` (NUMBER): The transaction amount.
    *   ... (other transaction details)
*   **`PROJECT_LOCATIONS`:** Contains information about restaurant locations, including:
    *   `ID` (INTEGER):  Unique identifier for the location.
    *   `PROJECT_ID` (INTEGER): Foreign key referencing `PROJECTS.ID`.
    *   `NAME` (VARCHAR):  The name of the location (e.g., the restaurant name).
    *   `LATITUDE` (FLOAT):  Latitude coordinate.
    *   `LONGITUDE` (FLOAT):  Longitude coordinate.
    *   ... (other location details)
*   **`PROJECTS`:**  Contains information about projects (likely representing groups of restaurants or venues), including:
    *   `ID` (INTEGER): Unique identifier for the project.
    *   `BRAND_ID` (INTEGER):  Foreign key referencing `BRANDS.ID`.
    *    `NAME` (VARCHAR)
    *   ... (other project details)
*   **`BRANDS`:** Contains information about restaurant brands, including:
    *   `ID` (INTEGER): Unique identifier for the brand.
    *   `VENUE_STYLE` (INTEGER):  Foreign key referencing `BRAND_TAGS.ID`.
    *   ... (other brand details)
*   **`BRAND_TAGS`:** Contains tags describing the cuisine type or style of a restaurant, including:
    *   `ID` (INTEGER): Unique identifier for the tag.
    *   `NAME` (VARCHAR):  The name of the tag (e.g., "Italian", "Vegan", "Fast Food").
    *   ... (other tag details)

**Relationships:**

*   `CREDIT_TRANSACTIONS`  one-to-many  `PROJECT_LOCATIONS` (via `PROJECT_LOCATION_ID`)
*   `PROJECT_LOCATIONS` one-to-many `PROJECTS` (via `PROJECT_ID`)
*   `PROJECTS` one-to-many `BRANDS` (via `BRAND_ID`)
*   `BRANDS` one-to-many `BRAND_TAGS` (via `VENUE_STYLE`)
