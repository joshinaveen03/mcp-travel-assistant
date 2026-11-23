"""
The agent loop for a multi-server setup.
"""

import os
import json
from openai import OpenAI

_client = None


def _get_client():
    global _client

    if _client is None:
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        if provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            api_key = os.getenv("OLLAMA_API_KEY", "ollama")
            _client = OpenAI(base_url=base_url, api_key=api_key)
        else:
            _client = OpenAI()

    return _client


def _get_model():
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "ollama":
        return os.getenv("OLLAMA_MODEL", "qwen3:1.7b")
    return os.getenv("OPENAI_MODEL", "gpt-4o")


async def collect_tools(sessions: dict):
    """List tools from every session and map each tool to its owner."""
    openai_tools = []
    owner_by_tool = {}

    for server_name, session in sessions.items():
        result = await session.list_tools()

        for tool in result.tools:
            owner_by_tool[tool.name] = server_name

            openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.input_schema,
                    },
                }
            )

    return openai_tools, owner_by_tool


async def run_agent(sessions: dict, query: str):
    """Run one query across all servers and return the final answer."""
    tools_used = []
    openai_tools, owner_by_tool = await collect_tools(sessions)

    messages = [
        {
            "role": "system",
            "content": (
               "Interpret flight dates in either YYYY/MM/DD or DD/MM/YYYY format. "
               "Convert them correctly before calling get_flights. "
            ),
        },
        {
            "role": "user",
            "content": query,
        },
    ]

    client = _get_client()
    model = _get_model()
    tools_param = openai_tools if openai_tools else None
    tool_choice_param = "auto" if openai_tools else None

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools_param,
        tool_choice=tool_choice_param,
    )

    assistant_message = response.choices[0].message
    messages.append(assistant_message)

    if not assistant_message.tool_calls:
        return assistant_message.content or "I could not find an answer.", tools_used

    for call in assistant_message.tool_calls:
        tool_name = call.function.name
        tools_used.append(tool_name)

        owner = owner_by_tool.get(tool_name)

        if owner is None:
            tool_result = f"Unknown tool: {tool_name}"
        else:
            try:
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                result = await sessions[owner].call_tool(
                    tool_name,
                    arguments=args,
                )

                tool_result = "\n".join(
                    item.text
                    for item in result.content
                    if hasattr(item, "text")
                )
            except Exception as e:
                tool_result = f"Error executing tool {tool_name}: {e}"

        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": tool_result or "The tool returned no details.",
            }
        )

    final_response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    answer = final_response.choices[0].message.content

    return answer or "The flight search completed, but no readable details were returned.", tools_used