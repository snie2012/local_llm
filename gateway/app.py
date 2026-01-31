import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from gateway.tools import TOOL_SPEC, execute_tool_call

LLAMA_CPP_URL = os.getenv("LLAMA_CPP_URL", "http://llama:8080")
MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "3"))

app = FastAPI(title="qwen-llama.cpp-gateway")


class ChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[dict[str, Any]]
    tools: list[dict[str, Any]] | None = None
    tool_choice: str | dict[str, Any] | None = None
    max_tokens: int | None = None
    temperature: float | None = None


async def request_llama_cpp(payload: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(f"{LLAMA_CPP_URL}/v1/chat/completions", json=payload)
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=response.text)
    return response.json()


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> dict[str, Any]:
    messages = list(request.messages)
    tools = request.tools or [TOOL_SPEC]
    tool_choice = request.tool_choice or "auto"

    for _ in range(MAX_TOOL_CALLS + 1):
        payload = {
            "model": request.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": tool_choice,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        response = await request_llama_cpp(payload)
        choice = response.get("choices", [{}])[0]
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls")

        if not tool_calls:
            return response

        messages.append(message)
        for tool_call in tool_calls:
            tool_message = execute_tool_call(tool_call)
            messages.append(tool_message)

    raise HTTPException(status_code=400, detail="tool call limit exceeded")
