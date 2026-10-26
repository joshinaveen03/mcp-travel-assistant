# 🤖 MCP Travel Assistant

An AI-powered multi-server **Model Context Protocol (MCP)** Travel Assistant.

The application provides a single conversational interface for weather, dates, flights, and Airbnb searches. The Streamlit frontend communicates with a FastAPI backend, while the backend connects to multiple MCP servers and lets OpenAI automatically select the appropriate tool.

---

## 🏗️ Architecture

```text
                         ┌──────────────────────────┐
                         │        USER              │
                         │  Natural Language Chat   │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │       STREAMLIT           │
                         │       app.py              │
                         │                          │
                         │  Attractive Chat UI      │
                         │  Server Status           │
                         │  Tool Usage              │
                         └────────────┬─────────────┘
                                      │
                                  HTTP/REST
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │        FASTAPI            │
                         │       backend.py          │
                         │                          │
                         │  GET  /tools             │
                         │  POST /chat               │
                         │  GET  /health             │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │       AI AGENT            │
                         │        agent.py           │
                         │                          │
                         │       OpenAI GPT         │
                         │  Automatic Tool Routing  │
                         └────────────┬─────────────┘
                                      │
                             MCP Client Sessions
                                      │
                     ┌────────────────┴────────────────┐
                     │                                 │
                     ▼                                 ▼
          ┌────────────────────┐             ┌────────────────────┐
          │    WEATHER MCP     │             │     AIRBNB MCP     │
          │     server.py      │             │  OpenBnB Server    │
          │                    │             │                    │
          │ get_weather        │             │ airbnb_search      │
          │ get_current_date   │             │ listing_details    │
          │ get_flights        │             │                    │
          └─────────┬──────────┘             └────────────────────┘
                    │
             External APIs
              ┌─────┴──────┐
              ▼            ▼
        OpenWeather       Tavily
```

---

# ✨ Features

## 🤖 AI Chatbot

Ask questions using normal language. The AI decides which MCP tool should be used.

Example:

```text
What's the weather in Delhi?
```

The agent can automatically select:

```text
get_weather
```

---

## 🌤️ Weather

Weather is provided through the local Weather MCP server and OpenWeather API.

Tool:

```text
get_weather
```

Example:

```text
What's the weather in Mumbai?
```

Returns information such as:

- City
- Country
- Weather condition
- Temperature
- Feels-like temperature
- Humidity
- Wind speed

---

## 📅 Current Date

Tool:

```text
get_current_date
```

Example:

```text
What is today's date?
```

Example response:

```text
Date: 2026-09-15. Day: Tuesday.
```

---

## ✈️ Flight Search

Tool:

```text
get_flights
```

The tool uses Tavily web search to find flight information.

Supported date formats:

```text
DD/MM/YYYY
YYYY/MM/DD
DD-MM-YYYY
YYYY-MM-DD
```

Examples:

```text
16/09/2026
2026/09/16
16-09-2026
2026-09-16
```

Example user query:

```text
Find flights from DEL to BOM on 16/09/2026.
```

The server normalizes the date before creating the Tavily search query.

---

## 🏠 Airbnb

The application connects to the OpenBnB Airbnb MCP server.

Available tools:

```text
airbnb_search
airbnb_listing_details
```

Example:

```text
Find me an Airbnb in Goa for 2 guests.
```

The AI automatically routes the request to the Airbnb MCP server.

---

# 🔌 Available MCP Tools

The application dynamically discovers MCP tools using:

```python
session.list_tools()
```

Current tools:

### Weather MCP

```text
get_weather
get_current_date
get_flights
```

### Airbnb MCP

```text
airbnb_search
airbnb_listing_details
```

The Streamlit sidebar displays the currently connected servers and discovered tools.

---

# 📁 Project Structure

```text
mcp-travel-assistant/
│
├── app.py
│       └── Streamlit chatbot frontend
│
├── backend.py
│       └── FastAPI backend and MCP session management
│
├── agent.py
│       └── OpenAI agent and MCP tool routing
│
├── models.py
│       └── Pydantic request/response models
│
├── server.py
│       └── Local Weather + Flight MCP server
│
├── .env
│       └── API keys
│
├── .gitignore
│       └── Files excluded from Git
│
├── requirements.txt
│       └── Python dependencies
│
└── README.md
        └── Project documentation
```

---

# 📄 File Responsibilities

| File | Responsibility |
|---|---|
| `app.py` | Streamlit user interface |
| `backend.py` | FastAPI API and MCP sessions |
| `agent.py` | OpenAI agent and tool calling |
| `models.py` | API data models |
| `server.py` | Weather and flight MCP tools |
| `.env` | Secret API keys |
| `requirements.txt` | Python dependencies |
| `README.md` | Documentation |

---

# 🧠 Agent Workflow

The main intelligence is implemented in:

```text
agent.py
```

The agent performs these steps:

```text
1. Receive user query
        ↓
2. Discover tools from all MCP servers
        ↓
3. Convert MCP tools to OpenAI function definitions
        ↓
4. Send query + tools to OpenAI
        ↓
5. OpenAI selects required tool
        ↓
6. Find MCP server that owns the tool
        ↓
7. Call MCP tool
        ↓
8. Receive tool result
        ↓
9. Send tool result back to OpenAI
        ↓
10. Generate final answer
        ↓
11. Return answer + tools_used
```

---

# 🔄 Multi-Server Tool Routing

The agent maintains an ownership map:

```python
owner_by_tool = {}
```

For example:

```text
get_weather
    ↓
weather

get_current_date
    ↓
weather

get_flights
    ↓
weather

airbnb_search
    ↓
airbnb

airbnb_listing_details
    ↓
airbnb
```

Therefore, the user does not need to specify which MCP server to use.

---

# 🔁 Multiple Tool Calls

The agent supports multiple rounds of tool calls.

For example:

```text
User
 ↓
OpenAI
 ↓
airbnb_search
 ↓
Airbnb result
 ↓
OpenAI
 ↓
airbnb_listing_details
 ↓
Listing details
 ↓
OpenAI
 ↓
Final answer
```

The agent limits processing to a maximum number of iterations to prevent an endless tool loop.

---

# ⚡ FastAPI Backend

The backend is implemented in:

```text
backend.py
```

It creates MCP sessions for:

```text
Weather
Airbnb
```

using:

```python
stdio_client()
ClientSession()
```

The MCP servers communicate with the FastAPI process through STDIO.

---

# 🌐 API Endpoints

## GET `/health`

Checks whether the backend is running.

Request:

```text
GET http://localhost:8000/health
```

Response:

```json
{
  "status": "ok",
  "servers": [
    "weather",
    "airbnb"
  ]
}
```

---

## GET `/tools`

Returns tools discovered from every MCP server.

Request:

```text
GET http://localhost:8000/tools
```

Example response:

```json
{
  "weather": [
    "get_weather",
    "get_current_date",
    "get_flights"
  ],
  "airbnb": [
    "airbnb_search",
    "airbnb_listing_details"
  ]
}
```

---

## POST `/chat`

Sends a user question to the AI agent.

Request:

```json
{
  "query": "What's the weather in Delhi?"
}
```

Response:

```json
{
  "answer": "The current weather in Delhi is...",
  "tools_used": [
    "get_weather"
  ]
}
```

---

# 📦 Pydantic Models

`models.py` defines the API contract.

## ChatRequest

```python
class ChatRequest(BaseModel):
    query: str
    server: str = "auto"
```

The `server` field is reserved for future use. Current routing is automatic.

---

## ChatResponse

```python
class ChatResponse(BaseModel):
    answer: str
    tools_used: list[str] = []
```

The frontend uses `tools_used` to show which MCP tools were used.

---

# 🌤️ Weather MCP Server

The local MCP server is:

```text
server.py
```

It loads environment variables:

```python
load_dotenv(".env")
```

The application supports MCP SDK compatibility:

```python
try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP
```

The server is named:

```text
Weather
```

---

# 🔧 Weather Tool

```python
@mcp.tool()
def get_weather(city: str) -> str:
```

The tool calls:

```text
https://api.openweathermap.org/data/2.5/weather
```

using the OpenWeather API.

The API is requested with:

```text
units = metric
```

so temperatures are returned in Celsius.

---

# 📅 Date Tool

```python
@mcp.tool()
def get_current_date() -> str:
```

It uses Python's `datetime` module and returns:

```text
Date: YYYY-MM-DD
Day: Weekday
```

---

# ✈️ Flight Tool

```python
@mcp.tool()
def get_flights(
    boarding_point: str,
    arrival_point: str,
    flight_date: str,
) -> str:
```

The tool:

```text
1. Validates the date
2. Supports multiple date formats
3. Converts the date to DD/MM/YYYY
4. Converts airport codes to uppercase
5. Builds a flight search query
6. Sends the query to Tavily
7. Returns search results
```

Example query generated:

```text
flights from DEL to BOM on 16/09/2026
```

The result includes:

```text
Route
Date
Title
Details
Booking URL
```

---

# 🏠 Airbnb MCP Server

The backend starts the Airbnb MCP server using:

```bash
npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt
```

The server provides:

```text
airbnb_search
airbnb_listing_details
```

No separate Python `server.py` implementation is required for Airbnb.

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

```env
OPENAI_API_KEY=your_openai_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### Important

Never commit `.env` to GitHub.

---

# 🚫 .gitignore

Recommended `.gitignore`:

```gitignore
.env
.venv/
venv/
__pycache__/
*.pyc
.streamlit/
```

---

# 📦 Installation

## 1. Create project directory

```bash
mkdir mcp-travel-assistant
cd mcp-travel-assistant
```

---

## 2. Create Python virtual environment

Windows:

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

---

## 3. Install Python dependencies

Create `requirements.txt`:

```text
streamlit
fastapi
uvicorn
requests
python-dotenv
pydantic
openai
mcp
```

Install:

```bash
pip install -r requirements.txt
```

---

# 🟢 Node.js / NPX Requirement

The Airbnb MCP server requires Node.js and `npx`.

Verify:

```bash
node --version
```

Then:

```bash
npx --version
```

If these commands are unavailable, install Node.js before starting the application.

---

# 🔑 API Key Setup

Add your API keys to:

```text
.env
```

Example:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENWEATHER_API_KEY=xxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx
```

Restart the backend after changing `.env`.

---

# ▶️ Run the Application

The application uses two terminals.

## Terminal 1 — FastAPI

```bash
python -m uvicorn backend:app --reload --port 8000
```

Expected:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

## Terminal 2 — Streamlit

```bash
streamlit run app.py
```

Streamlit normally opens:

```text
http://localhost:8501
```

---

# 🧪 Test the Backend

Before using the Streamlit frontend, test:

```text
http://localhost:8000/health
```

Then:

```text
http://localhost:8000/tools
```

The `/tools` endpoint should return the connected MCP tools.

---

# 💬 Example Questions

## Weather

```text
What's the weather in Delhi?
```

```text
What's the weather in Mumbai?
```

```text
What's the temperature in London?
```

---

## Date

```text
What is today's date?
```

```text
What day is today?
```

---

## Flights

```text
Find flights from DEL to BOM on 16/09/2026.
```

```text
Search flights from Delhi to Mumbai on 2026/09/16.
```

```text
Find flights from BLR to DEL on 20/09/2026.
```

---

## Airbnb

```text
Find an Airbnb in Goa for 2 guests.
```

```text
Find Airbnb properties in Mumbai.
```

```text
Show me Airbnb listings in Bangalore.
```

---

# 🧪 Example End-to-End Request

User asks:

```text
What's the weather in Delhi?
```

### Step 1 — Streamlit

The frontend sends:

```http
POST /chat
```

with:

```json
{
  "query": "What's the weather in Delhi?"
}
```

### Step 2 — FastAPI

FastAPI creates MCP sessions.

```text
weather session
airbnb session
```

### Step 3 — Agent

The agent discovers:

```text
get_weather
get_current_date
get_flights
airbnb_search
airbnb_listing_details
```

### Step 4 — OpenAI

OpenAI decides:

```text
get_weather
```

### Step 5 — MCP

The agent finds the owner:

```text
get_weather → weather
```

and executes:

```python
sessions["weather"].call_tool(
    "get_weather",
    arguments={"city": "Delhi"}
)
```

### Step 6 — OpenWeather

The Weather MCP server calls OpenWeather.

### Step 7 — Result

The weather result is returned to the agent.

### Step 8 — Final Answer

OpenAI creates the user-friendly response.

### Step 9 — FastAPI

FastAPI returns:

```json
{
  "answer": "...",
  "tools_used": [
    "get_weather"
  ]
}
```

### Step 10 — Streamlit

The UI displays:

```text
👤 You
What's the weather in Delhi?

🤖 MCP Assistant
Current weather in Delhi is...

Tools used:
🔧 get_weather
```

---

# 🔄 Flight Request Flow

Example:

```text
Find flights from DEL to BOM on 16/09/2026.
```

Flow:

```text
Streamlit
    ↓
FastAPI /chat
    ↓
agent.py
    ↓
OpenAI
    ↓
get_flights
    ↓
Weather MCP server
    ↓
Validate date
    ↓
Normalize date
    ↓
Tavily API
    ↓
Flight search results
    ↓
OpenAI
    ↓
Final answer
    ↓
Streamlit
```

---

# 🏠 Airbnb Request Flow

Example:

```text
Find an Airbnb in Goa for 2 guests.
```

Flow:

```text
Streamlit
    ↓
FastAPI
    ↓
agent.py
    ↓
OpenAI
    ↓
airbnb_search
    ↓
Airbnb MCP Server
    ↓
Search results
    ↓
OpenAI
    ↓
Final answer
```

For detailed information about a selected property:

```text
airbnb_search
       ↓
listing result
       ↓
airbnb_listing_details
       ↓
detailed property information
```

---

# 🛠️ Error Handling

The backend validates empty queries.

If the user submits an empty query:

```text
HTTP 400
```

Response:

```text
Query cannot be empty.
```

MCP connection errors are returned as:

```text
HTTP 502
```

The frontend displays an appropriate error message.

The agent also handles:

- OpenAI API errors
- Invalid tool arguments
- Unknown tools
- MCP tool failures
- Empty MCP responses
- Invalid flight dates
- Missing API keys

---

# 🔍 Troubleshooting

## Backend Offline

If Streamlit says:

```text
Backend Offline
```

run:

```bash
python -m uvicorn backend:app --reload --port 8000
```

---

## OpenAI API Key Error

Check:

```env
OPENAI_API_KEY=...
```

in `.env`.

---

## OpenWeather Error

Check:

```env
OPENWEATHER_API_KEY=...
```

---

## Tavily Error

Check:

```env
TAVILY_API_KEY=...
```

---

## `npx` Not Found

Check:

```bash
node --version
npx --version
```

Install Node.js if either command fails.

---

## Airbnb MCP Not Starting

Try manually:

```bash
npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt
```

Then restart FastAPI.

---

## MCP Tools Missing

Open:

```text
http://localhost:8000/tools
```

Expected:

```json
{
  "weather": [
    "get_weather",
    "get_current_date",
    "get_flights"
  ],
  "airbnb": [
    "airbnb_search",
    "airbnb_listing_details"
  ]
}
```

If the tools are missing, inspect the FastAPI terminal for MCP startup errors.

---

# 🔒 Security

Never hard-code API keys.

### ❌ Incorrect

```python
OPENAI_API_KEY = "sk-xxxxxxxx"
```

### ✅ Correct

`.env`:

```env
OPENAI_API_KEY=sk-xxxxxxxx
```

Python:

```python
os.getenv("OPENAI_API_KEY")
```

Also add `.env` to `.gitignore`.

---

# 🎓 MCP Concepts Demonstrated

This project demonstrates:

### 1. MCP Server

A server exposes capabilities as tools.

```text
Weather MCP
Airbnb MCP
```

### 2. MCP Client

FastAPI creates:

```python
ClientSession
```

to communicate with MCP servers.

### 3. STDIO Transport

The local Weather MCP server is launched using Python:

```python
StdioServerParameters(
    command=sys.executable,
    args=["server.py"],
)
```

The Airbnb MCP server is launched using:

```python
StdioServerParameters(
    command="npx",
    args=[
        "-y",
        "@openbnb/mcp-server-airbnb",
        "--ignore-robots-txt",
    ],
)
```

### 4. Tool Discovery

The agent discovers tools dynamically:

```python
await session.list_tools()
```

### 5. Tool Execution

The agent executes tools:

```python
await session.call_tool(...)
```

### 6. AI Tool Calling

OpenAI determines which tool should be used based on the user's request.

### 7. Multi-Server MCP

A single AI agent can access tools from multiple independent MCP servers.

---

# 🧩 Why MCP?

Without MCP, an application often needs custom integration logic for every external service.

With MCP:

```text
AI Agent
   │
   ├── Weather MCP
   ├── Flight MCP
   ├── Airbnb MCP
   ├── Maps MCP
   ├── Hotel MCP
   └── Payment MCP
```

Tools can be discovered and called through a common protocol.

This makes the architecture easier to extend.

---

# 🚀 Future Enhancements

Possible improvements include:

- 💬 Persistent multi-turn conversation memory
- 👤 User authentication
- 🔐 Login system
- 🗃️ Conversation database
- 🗺️ Maps MCP
- 🚆 Train search MCP
- 🏨 Hotel search MCP
- 🚕 Cab/transport MCP
- 💱 Currency conversion
- 🌦️ Weather forecast
- ✈️ Dedicated flight API integration
- 📍 Location-aware travel recommendations
- 🧾 Booking workflows
- 🔔 Travel alerts
- 📊 MCP monitoring dashboard
- 🧠 RAG travel knowledge base
- 📱 Mobile-responsive UI
- 📈 Usage analytics

---

# 🧠 Recommended Next Architecture

For a production-ready version:

```text
                         ┌─────────────────────┐
                         │      Streamlit      │
                         │    Chat Frontend    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI      │
                         │   Authentication   │
                         │   Session Manager  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     AI Agent        │
                         │                     │
                         │ OpenAI + MCP        │
                         │ Conversation Memory │
                         └──────────┬──────────┘
                                    │
            ┌───────────────────────┼──────────────────────┐
            ▼                       ▼                      ▼
      Weather MCP             Airbnb MCP             Maps MCP
            │                       │                      │
            ▼                       ▼                      ▼
      OpenWeather               Airbnb                 Maps
            │
            ▼
         Tavily
```

---

# 📌 Quick Start

### 1. Activate environment

```bash
.venv\Scripts\activate
```

### 2. Start FastAPI

```bash
python -m uvicorn backend:app --reload --port 8000
```

### 3. Start Streamlit

```bash
streamlit run app.py
```

### 4. Open the application

```text
http://localhost:8501
```

### 5. Try:

```text
What's the weather in Delhi?
```

Then:

```text
Find flights from DEL to BOM on 16/09/2026.
```

Then:

```text
Find an Airbnb in Goa for 2 guests.
```

---

# 🏆 Project Summary

The MCP Travel Assistant demonstrates how to build an AI application that connects **multiple MCP servers** to a single conversational interface.

The core architecture is:

```text
User
 ↓
Streamlit
 ↓
FastAPI
 ↓
OpenAI Agent
 ↓
MCP Tool Discovery
 ↓
Automatic Tool Selection
 ↓
MCP Server
 ↓
External API
 ↓
Tool Result
 ↓
OpenAI
 ↓
Final Answer
```

The project combines:

```text
Streamlit
+
FastAPI
+
OpenAI
+
MCP
+
OpenWeather
+
Tavily
+
Airbnb MCP
```

to create a practical AI-powered travel assistant.

---

## 📄 License

This project is intended primarily for educational and demonstration purposes.

If publishing publicly, add an appropriate license such as MIT and review the terms of the external APIs and MCP packages used by the project.
