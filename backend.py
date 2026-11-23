import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agent import run_agent
from models import ChatRequest, ChatResponse


load_dotenv(".env")

provider = os.getenv("LLM_PROVIDER", "ollama").lower()
if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not found in .env")


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

WEATHER = StdioServerParameters(
    command=sys.executable,
    args=["-u", os.path.join(CURRENT_DIR, "server.py")],
    cwd=CURRENT_DIR,
)

AIRBNB = StdioServerParameters(
    command="npx.cmd" if sys.platform == "win32" else "npx",
    args=[
        "-y",
        "@openbnb/mcp-server-airbnb",
        "--ignore-robots-txt",
    ],
    cwd=CURRENT_DIR,
)


app = FastAPI(
    title="MCP Travel Assistant",
    version="1.0.0",
)


async def _with_sessions(function):
    """Open MCP sessions, execute the function, then close the sessions."""
    async with (
        stdio_client(WEATHER) as (weather_reader, weather_writer),
        stdio_client(AIRBNB) as (airbnb_reader, airbnb_writer),
    ):
        async with (
            ClientSession(weather_reader, weather_writer) as weather,
            ClientSession(airbnb_reader, airbnb_writer) as airbnb,
        ):
            await weather.initialize()
            await airbnb.initialize()

            sessions = {
                "weather": weather,
                "airbnb": airbnb,
            }

            return await function(sessions)


@app.get("/tools")
async def list_tools():
    async def get_available_tools(sessions):
        available_tools = {}

        for server_name, session in sessions.items():
            result = await session.list_tools()
            available_tools[server_name] = [
                tool.name for tool in result.tools
            ]

        return available_tools

    try:
        return await _with_sessions(get_available_tools)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to connect to MCP servers: {error}",
        ) from error


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    async def process_chat(sessions):
        answer, tools_used = await run_agent(
            sessions,
            request.query.strip(),
        )

        return ChatResponse(
            answer=answer or "No readable answer was returned.",
            tools_used=tools_used,
        )

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    try:
        return await _with_sessions(process_chat)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Chat request failed: {error}",
        ) from error


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "servers": ["weather", "airbnb"],
    }