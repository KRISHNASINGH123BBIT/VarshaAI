import os

import requests
import ollama

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="VarshaAI Weather Assistant",
    description="An AI-powered weather chatbot",
    version="1.0.0"
)


# Configure Ollama.
# Set OLLAMA_HOST in Render to the address of a reachable Ollama server.
OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:0.5b"
)

ollama_client = ollama.Client(host=OLLAMA_HOST)


# Validate incoming requests.
class WeatherRequest(BaseModel):
    prompt: str = Field(
        default="What is the weather?",
        min_length=1,
        max_length=1000
    )
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


# Homepage
@app.get("/")
def home():
    return {
        "status": "success",
        "message": "VarshaAI Weather Assistant is running!",
        "docs": "/docs",
        "weather_endpoint": "/ask_weather"
    }


# Health check
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "VarshaAI Weather Assistant"
    }


# Weather chatbot endpoint
@app.post("/ask_weather")
def ask_weather(data: WeatherRequest):

    try:
        # 1. Detect the location using OpenStreetMap
        osm_url = "https://nominatim.openstreetmap.org/reverse"

        osm_params = {
            "format": "jsonv2",
            "lat": data.lat,
            "lon": data.lon,
            "zoom": 14,
            "addressdetails": 1
        }

        osm_response = requests.get(
            osm_url,
            params=osm_params,
            headers={
                "User-Agent": "VarshaAI-WeatherAssistant/1.0"
            },
            timeout=15
        )

        osm_response.raise_for_status()

        osm_data = osm_response.json()
        address = osm_data.get("address", {})

        location_name = (
            address.get("suburb")
            or address.get("neighbourhood")
            or address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("county")
            or "your area"
        )

        # 2. Fetch current weather from Open-Meteo
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": data.lat,
            "longitude": data.lon,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "is_day,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "timezone": "auto"
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=15
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()
        current = weather_data.get("current")

        if not current:
            raise HTTPException(
                status_code=502,
                detail="Current weather data is unavailable."
            )

        temperature = current.get("temperature_2m")
        wind_speed = current.get("wind_speed_10m")
        humidity = current.get("relative_humidity_2m")
        feels_like = current.get("apparent_temperature")
        precipitation = current.get("precipitation")
        weather_code = current.get("weather_code")

        if temperature is None or wind_speed is None:
            raise HTTPException(
                status_code=502,
                detail="Incomplete weather data received."
            )

        # 3. Prepare reliable weather context for the AI
        ai_context = f"""
You are VarshaAI, a helpful weather assistant.

The user asks: {data.prompt}

Verified current weather information:
Location: {location_name}
Temperature: {temperature} degrees Celsius
Feels like: {feels_like} degrees Celsius
Relative humidity: {humidity} percent
Wind speed: {wind_speed} km/h
Precipitation: {precipitation} mm
Weather code: {weather_code}

Instructions:
- Answer the user's actual question.
- Use the supplied weather information when relevant.
- Give practical advice when appropriate.
- Do not invent forecasts or weather measurements.
- If the user asks about future weather, explain that only
  current conditions were retrieved by this request.
- If a measurement is unavailable, say so.
- Keep the response clear, friendly, and concise.
"""

        # 4. Generate an AI response using Ollama
        try:
            ai_response = ollama_client.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": ai_context
                    }
                ]
            )

            reply = ai_response["message"]["content"]

        except Exception as exc:
            print(f"Ollama error: {exc}")

            raise HTTPException(
                status_code=503,
                detail=(
                    "The weather service is available, but the AI "
                    "assistant is currently unavailable. Check the "
                    "Ollama server and model configuration."
                )
            )

        # 5. Return the response to the frontend
        return {
            "status": True,
            "location_detected": location_name,
            "weather": {
                "temperature_c": temperature,
                "feels_like_c": feels_like,
                "humidity_percent": humidity,
                "wind_speed_kmh": wind_speed,
                "precipitation_mm": precipitation,
                "weather_code": weather_code
            },
            "reply": reply
        }

    except HTTPException:
        raise

    except requests.RequestException as exc:
        print(f"External API error: {exc}")

        raise HTTPException(
            status_code=502,
            detail=(
                "Could not retrieve location or weather data. "
                "Please try again later."
            )
        )

    except Exception as exc:
        print(f"Unexpected error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred."
        )
