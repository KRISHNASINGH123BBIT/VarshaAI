# VarshaAI - Weather Assistant

A lightweight weather API built with **Python, FastAPI, Ollama, and Qwen2.5:0.5B**. It retrieves weather information for supplied geographic coordinates and uses a locally running language model to generate a simple, conversational response.

## Overview

### Problem Statement
Weather API responses can be difficult for some users to understand. This project combines live weather data with a local language model to make weather information easier to interpret.

### Solution
The application:
- Accepts a user prompt and latitude/longitude.
- Identifies the approximate location using OpenStreetMap Nominatim.
- Retrieves current weather data using Open-Meteo.
- Uses Qwen2.5:0.5B through Ollama to generate a natural-language response.
- Returns a structured JSON response through FastAPI.

## Features

- **Local AI inference:** Uses Qwen2.5:0.5B through Ollama.
- **Weather integration:** Retrieves current weather data from Open-Meteo.
- **Location lookup:** Uses OpenStreetMap Nominatim reverse geocoding.
- **REST API:** Provides a POST endpoint for weather questions.
- **Input validation:** Checks that latitude and longitude are provided.
- **Structured responses:** Returns JSON with status, location, and reply.

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| API framework | FastAPI |
| ASGI server | Uvicorn |
| Local AI runtime | Ollama |
| Language model | Qwen2.5:0.5B |
| HTTP requests | Requests |
| Geocoding | OpenStreetMap Nominatim |
| Weather data | Open-Meteo |

## Architecture

User / API Client  
↓  
FastAPI — `POST /ask_weather`  
↓  
Validate latitude and longitude  
↓  
OpenStreetMap Nominatim — resolve location  
↓  
Open-Meteo — retrieve current weather  
↓  
Ollama + Qwen2.5:0.5B — generate a conversational reply  
↓  
JSON response returned to the client

## Prerequisites

- Python 3.10 or newer recommended.
- Ollama installed on your computer.
- Internet connection for external weather and geocoding services.
- Sufficient RAM and storage for the selected local model.

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
python -m pip install fastapi uvicorn requests ollama
```

### 4. Install and download the AI model

Install Ollama from:

https://ollama.com/download

Download the model:

```bash
ollama pull qwen2.5:0.5b
```

Verify the installation:

```bash
ollama list
```

### 5. Start the application

If your Python file is named `main.py`:

```bash
uvicorn main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Documentation

### Endpoint

`POST /ask_weather`

### Request Body

```json
{
  "prompt": "Explain the current weather in simple words",
  "lat": 22.5726,
  "lon": 88.3639
}
```

The example coordinates represent Kolkata, India.

### Example Response

The following is an illustrative response; actual wording and weather values depend on the live APIs and model output.

```json
{
  "status": true,
  "location_detected": "Kolkata",
  "reply": "It is currently 29°C in Kolkata, with winds of 10 km/h. It feels like a warm day."
}
```

### Missing Coordinates

If latitude or longitude is missing, the API returns an error message indicating that both coordinates are required.

## Testing

1. Start Ollama and ensure the Qwen model is available.
2. Start the FastAPI server.
3. Open `/docs` in your browser.
4. Select `POST /ask_weather`.
5. Click **Try it out** and submit the sample JSON request.
6. Verify that the response contains `status`, `location_detected`, and `reply`.

## Project Structure

```text
project/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Limitations

- An internet connection is required for weather and geocoding requests.
- The application uses the coordinates supplied by the client; it does not automatically detect the user's device location.
- Location naming depends on the fields returned by the geocoding service.
- The language model may occasionally produce inaccurate or imprecise wording.
- The current implementation does not include authentication, rate limiting, or automated tests.

## Privacy and Security

- The language model runs locally through Ollama.
- Do not commit API keys, passwords, private configuration files, or sensitive data.
- External geocoding and weather services receive the coordinates needed to fulfil requests.
- Review third-party service usage policies before deployment.

## Future Improvements

- Add automated tests and stronger input validation.
- Add caching and request timeouts.
- Improve weather condition descriptions using weather codes.
- Add frontend integration and deployment instructions.
- Introduce monitoring, rate limiting, and API authentication.

## License

Choose and add an appropriate open-source license before publishing the repository.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Ollama](https://ollama.com/)
- [Qwen](https://github.com/QwenLM/Qwen2.5)
- [Open-Meteo](https://open-meteo.com/)
- [OpenStreetMap Nominatim](https://nominatim.org/)
