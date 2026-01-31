from gateway.tools import TOOL_SPEC, execute_tool_call


def test_tool_spec_has_web_fetch():
    assert TOOL_SPEC["function"]["name"] == "web_fetch"
    assert "url" in TOOL_SPEC["function"]["parameters"]["properties"]


def test_execute_tool_call_handles_missing_url():
    tool_call = {"id": "1", "function": {"name": "web_fetch", "arguments": "{}"}}
    message = execute_tool_call(tool_call)
    assert message["role"] == "tool"
    assert "Missing required argument" in message["content"]
