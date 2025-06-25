# Simple MCP Chat CLient

Connect to an MCP server from your terminal and chat using Gemini.

## Examples:

Python server file:

```bash
uv run client.py example-server.py
```

COnnect to an MCP server package

```bash
uv run client.py @modelcontextprotocol/server-sequential-thinking
```

Remember to set `GEMINI_API_KEY` in .env.

## TODO:

- [ ] HTTP servers not working yet, only SSE ones
