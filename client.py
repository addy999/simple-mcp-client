import asyncio
import json
import logging

import colorlog
import typer
from fastmcp import Client
from litellm import async_completion_with_fallbacks
from litellm.utils import ModelResponse
from mcp.types import Resource, Tool
from typing_extensions import Annotated


logging.basicConfig(level=logging.WARNING)

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s:%(name)s:%(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.name = "MCP Client"
logger.addHandler(handler)
logger.propagate = False


MODELS = [
    "gemini/gemini-2.5-pro",
    "gemini/gemini-2.0-flash",
]


def to_snake_case(string: str) -> str:
    """Convert a string to snake_case."""
    return "_".join(word.lower() for word in string.split())


def convert_tool_to_gemini_tool(tool: Tool):
    """Convert a FastMCP tool to a Gemini-compatible tool."""

    params = tool.inputSchema.copy()
    params.pop("title", "")

    properties = params.pop("properties")
    for prop, data in properties.items():
        data.pop("title", "")
    params["properties"] = properties

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": params,
        },
    }


def create_resource_fetcher_tools(resources: list[Resource]):
    """Create tools that fetch data from resources."""

    return [
        {
            "type": "function",
            "function": {
                "name": to_snake_case(resource.name),
                "description": resource.description,
                "parameters": {
                    "required": [],
                    "type": "object",
                },
            },
        }
        for resource in resources
    ]


class MyClient:
    def __init__(self, *args, **kwargs):
        self.client = Client(*args, **kwargs)
        self.tools: list[dict] = []
        self.messages: list[dict] = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Use the tools provided to answer user queries. You can call tools as needed without asking the user.",
            }
        ]
        self.resources: dict[str, str] = {}  # name to uri mapping

    async def fetch_resource(self, name: str) -> str:
        async with self.client as client:
            uri = self.resources.get(name)
            result = await client.read_resource(uri)  # type: ignore
            return result[0].text  # type: ignore

    async def _load_tools(self):
        self.tools = []
        async with self.client:
            tools = await self.client.list_tools()
            for tool in tools:
                self.tools.append(convert_tool_to_gemini_tool(tool))

            try:
                resources = await self.client.list_resources()
                self.resources = {
                    to_snake_case(res.name): str(res.uri) for res in resources
                }
                self.tools.extend(create_resource_fetcher_tools(resources))
            except Exception as e:
                logger.error(f"Error loading resources: {e}")

    async def process_query(self, query: str):

        logger.debug(f"Processing query: {query}")

        query = query.strip()
        if not query:
            return "Query cannot be empty."

        self.messages.append({"role": "user", "content": query})

        response: ModelResponse = await async_completion_with_fallbacks(
            model=MODELS[0],
            fallbacks=MODELS[1:],
            messages=self.messages,
            tools=self.tools,
        )  # type: ignore

        text_response = response.choices[0].message.content

        if response.choices[0].message.tool_calls:
            call = response.choices[0].message.tool_calls[0]
            tool_name = call.function.name
            tool_args = call.function.arguments

            print(f"Calling tool: {tool_name} with arguments: {tool_args}")

            self.messages.append(
                {
                    "role": "assistant",
                    "content": f"Calling tool: {tool_name} with arguments: {tool_args}",
                }
            )

            if tool_name in self.resources:
                tool_response = await self.fetch_resource(tool_name)
                return await self.process_query(tool_response)

            else:
                # Call the tool using the FastMCP client
                async with self.client:
                    result = await self.client.call_tool(
                        tool_name, json.loads(tool_args)
                    )
                    tool_response = result[0].text
                    if tool_response.startswith("{"):
                        return await self.process_query(tool_response)
                    else:
                        text_response = tool_response

        self.messages.append(
            {
                "role": "assistant",
                "content": text_response,
            }
        )

        return text_response

    async def run(self):
        """Run the client to process queries interactively."""
        while True:
            query = input("Enter your query (or 'exit' to quit): ")
            if query.lower() == "exit":
                break
            response = await self.process_query(query)
            logger.info(f" Response: {response}")


def main(
    server: Annotated[
        str,
        typer.Argument(
            help="Server to connect to. Can be a server .js file, a .py file, or a package name. For example: '@modelcontextprotocol/server-sequential-thinking'"
        ),
    ],
):
    """Main entry point for the client."""

    async def run():
        client = MyClient(server)
        await client._load_tools()
        logger.info(f"Tools available: {client.tools}")
        await client.run()

    asyncio.run(run())


if __name__ == "__main__":
    typer.run(main)  # For CLI usage
