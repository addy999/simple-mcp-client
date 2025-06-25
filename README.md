# Simple MCP Chat CLient

Connect to an MCP server from your terminal and chat using Gemini.

This project uses uv instead of pip, simply run any of the following commands and all packages will be installed and a .venv will be created automatically.

## Capabilities

- [x] Supports any MCP server package
- [x] Supports stdio and sse transport
- [x] Supports one tool calling at a time
- [x] Supports resources with an inline tool implementation
- [ ] MCP server prompts not yet supported

## Examples:

Python server file:

```bash
>> uv run client.py example-server.py

INFO     Starting MCP server 'ExampleServer' with transport 'stdio' example-server.py:1246

>> Enter your query (or 'exit' to quit): Hi what can you do?
INFO:MCP Client: Response: I can fetch the current weather for a city, or I can tell you the current city.

>> Enter your query (or 'exit' to quit): can you tell me the weather in the current city?
Calling tool: get_current_city with arguments: {}
Calling tool: fetch_weather with arguments: {"city": "Toronto"}

INFO:MCP Client: Response: OK. The weather in Toronto, Canada is partly cloudy. The temperature is 29.4 degrees Celsius, but it feels like 32.4 degrees Celsius. The wind is blowing from the North at 4.7 kilometers per hour.
```

You can also connect to an MCP server package

```bash
uv run client.py @modelcontextprotocol/server-sequential-thinking
```

Remember to set `GEMINI_API_KEY` in .env.

Only a server argument is needed, see `uv run client.py --help`.

## TODO:

- [ ] HTTP servers not working yet, only SSE ones
- [ ] Continous tool calls sometimes don't run
