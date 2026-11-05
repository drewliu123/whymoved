"""Offline MCP handshake: starts the local server; never requests SEC data."""
import asyncio
import json
import sys
from pathlib import Path

# Reuse installed evaluation packages with the normal local interpreter.
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "research/edgartools-eval-venv/lib/python3.12/site-packages"))
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=[str(Path(__file__).with_name("run_mcp.py"))])
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            prompts = await session.list_prompts()
            invalid = await session.call_tool("edgar_filing", {"input": "not-an-accession"})
            payload = {
                "validation_scope": "offline initialize, list_tools, list_prompts, invalid input; no SEC request",
                "server": initialized.serverInfo.model_dump(mode="json"),
                "tool_count": len(tools.tools),
                "tools": [{"name": t.name, "inputSchema": t.inputSchema} for t in tools.tools],
                "prompts": [p.name for p in prompts.prompts],
                "invalid_input_response": invalid.model_dump(mode="json"),
            }
            out = Path(__file__).with_name("mcp-smoke-result.json")
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({"server": payload["server"], "tool_count": payload["tool_count"],
                              "prompts": payload["prompts"], "result_path": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
