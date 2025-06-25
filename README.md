# Simple MCP Chat CLient

Connect to an MCP server from your terminal and chat using Gemini.

This project uses uv instead of pip, simply run any of the following commands and all packages will be installed and a .venv will be created automatically.

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

Only a server argument is needed, see `uv run client.py --help`.

## TODO:

- [ ] HTTP servers not working yet, only SSE ones
- [ ] Continous tool calls sometimes don't run
