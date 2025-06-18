# TODO
# One way to approach the restaurant recommendation problem.
# 
# 1. Get automatic location of user (to be provided by mobile phone) - this will be lat and lon - converted to location name
#    https://developers.google.com/maps/documentation/geocoding/requests-reverse-geocoding
#    or ramen near 46.207035, 6.141339 within a 1 kilometre radius in Google Search
# 2. Ask the user the type of food they want to eat
#    https://ai.google.dev/gemini-api/docs/text-generation?lang=python
# 3. Use the lat and lon to get the restaurants that serve the type of food using Google Seach API - using Gemini
# 4. Refine (reviews, location, etc) using Google Maps API - add to context/prompt
