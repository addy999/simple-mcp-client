from fastmcp import FastMCP
import httpx

mcp = FastMCP("ExampleServer")


# 1. Define a Tool:
# Tools perform actions, can be computationally expensive, and have side effects.
# The docstring provides the LLM with a description of the tool.
@mcp.tool()
async def fetch_weather(city: str) -> dict:
    """Fetch current weather for a specified city."""
    API_KEY = "API_KEY_HERE"  # free api key from https://www.weatherapi.com/
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=no"
        )
        return response.json()


# 2. Define a Resource:
# Resources expose data, similar to GET endpoints, intended for quick queries without side effects.
@mcp.resource("location://current")
def get_current_city() -> str:
    """Returns the name of the current city."""
    return "Toronto"


# 3. Define a Prompt:
# Prompts are reusable templates to guide LLM interactions.
@mcp.prompt(name="Code Review Assistant")
def review_code(code: str) -> str:
    """Generates a comprehensive review for the provided code snippet."""
    return f"Please provide a detailed code review for this Python code: \n\n{code}"


if __name__ == "__main__":
    mcp.run(
        # transport="http",
        # path="/mcp",
    )
