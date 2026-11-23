"""Pydantic models for the API's request and response shapes."""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's message")
    # The agent sees tools from all servers and routes automatically,
    # so a server does not have to be chosen. Kept for future use.
    server: str = Field("auto", description="Reserved. Routing is automatic.")


class ChatResponse(BaseModel):
    answer: str
    tools_used: list[str] = []