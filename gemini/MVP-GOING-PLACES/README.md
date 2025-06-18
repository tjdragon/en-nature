## Prerequisites

- Python 3.7 or higher
- Google Gemini API key
- Google Maps API key with Places API enabled
- Internet connection lol 

## Installation

Install the required dependencies ( see the imports ) 
```
pip install google-generativeai google-genai python-dotenv requests ipython
```

Create a `.env` file in the project root directory with your API keys:
```
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GOOGLE_API_KEY=your_google_gemini_api_key
```

## Usage

Run the script:
```bash
python mvp-places-ground-with-logs.py
```

## Default Location

If no location is specified, the assistant uses the **Flatiron Building in New York** as the default location.

## Logging

The script logs all activities to `mvp_places.log` for debugging purposes. The log includes:
- API requests and responses
- Function calls and their parameters
- Error messages and exceptions
- User inputs and system outputs
