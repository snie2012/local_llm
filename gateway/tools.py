import json
from typing import Any

import httpx

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "web_fetch",
        "description": "Fetch a URL from the internet and return the text body.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch.",
                }
            },
            "required": ["url"],
        },
    },
}


def _load_arguments(tool_call: dict[str, Any]) -> dict[str, Any]:
    arguments = tool_call.get("function", {}).get("arguments", "{}")
    if isinstance(arguments, dict):
        return arguments
    return json.loads(arguments or "{}")


def _fetch_url(url: str) -> str:
    with httpx.Client(timeout=20) as client:
        response = client.get(url)
    response.raise_for_status()
    return response.text


def execute_tool_call(tool_call: dict[str, Any]) -> dict[str, Any]:
    function = tool_call.get("function", {})
    name = function.get("name")
    if name != "web_fetch":
        return {
            "role": "tool",
            "tool_call_id": tool_call.get("id"),
            "name": name,
            "content": f"Unsupported tool: {name}",
        }

    args = _load_arguments(tool_call)
    url = args.get("url")
    if not url:
        content = "Missing required argument: url"
    else:
        content = _fetch_url(url)

    return {
        "role": "tool",
        "tool_call_id": tool_call.get("id"),
        "name": name,
        "content": content,
    }
