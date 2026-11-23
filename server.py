"""
Local MCP server for the capstone app.
Exposes a real weather tool backed by the OpenWeather API, over STDIO.
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime


load_dotenv(".env")

try:
    # MCP SDK 2.x (FastMCP was renamed to MCPServer)
    from mcp.server.mcpserver import MCPServer as _Server

except ImportError:
    # MCP SDK 1.x fallback
    from mcp.server.fastmcp import FastMCP as _Server

mcp = _Server("Weather")

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

@mcp.tool()
def get_weather(city: str) -> str:
    """Gets the current weather for a city using the OpenWeather API.
    city should be a plain city name, for example 'Delhi' or 'London'."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "OPENWEATHER_API_KEY is not set on the server."
    try:
        params = {"q": city, "appid": api_key, "units": "metric"}
        resp = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        if resp.status_code == 404:
            return f"City '{city}' not found."
        resp.raise_for_status()
        data = resp.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        name = data.get("name", city)
        country = data.get("sys", {}).get("country", "")
        return (
            f"Weather in {name}, {country}: {desc}. "
            f"Temperature {temp} C (feels like {feels} C), "
            f"humidity {humidity}%, wind {wind} m/s."
        )
    except Exception as e:
        return f"Error fetching weather for {city}: {e}"

@mcp.tool()
def get_current_date() -> str:
    """Returns the current date and day."""

    now = datetime.now()

    return (
        f"Date: {now.strftime('%Y-%m-%d')}. "
        f"Day: {now.strftime('%A')}."
    )

# Tavily API
TAVILY_URL = "https://api.tavily.com/search"


@mcp.tool()
def get_flights(
    boarding_point: str,
    arrival_point: str,
    flight_date: str,
) -> str:
    """Search flights. Accept dates in DD/MM/YYYY or YYYY/MM/DD format."""

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return "TAVILY_API_KEY is not set."

    date_value = flight_date.strip()
    parsed_date = None

    for date_format in ("%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            parsed_date = datetime.strptime(date_value, date_format)
            break
        except ValueError:
            continue

    if parsed_date is None:
        return (
            "Invalid date. Please use DD/MM/YYYY, "
            "for example 16/09/2026."
        )

    departure = boarding_point.strip().upper()
    arrival = arrival_point.strip().upper()
    normalized_date = parsed_date.strftime("%d/%m/%Y")

    query = (
        f"flights from {departure} to {arrival} "
        f"on {normalized_date}"
    )

    try:
        response = requests.post(
            TAVILY_URL,
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": 5,
            },
            timeout=20,
        )

        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if not results:
            return f"No flight information found for {query}."

        output = []

        for result in results:
            output.append(
                f"Route: {departure} to {arrival}\n"
                f"Date: {normalized_date}\n"
                f"Title: {result.get('title', 'Unknown')}\n"
                f"Details: {result.get('content', 'No details available')}\n"
                f"Booking URL: {result.get('url', 'Unavailable')}"
            )

        return "\n\n------------------------------\n\n".join(output)

    except requests.RequestException as error:
        return f"Flight search request failed: {error}"
    except ValueError:
        return "Tavily returned an invalid response."

if __name__ == "__main__":
    mcp.run()