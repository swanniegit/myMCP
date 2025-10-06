from fastmcp import FastMCP

# Create a FastMCP server
mcp = FastMCP("Basic Demo Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

@mcp.resource("greeting://welcome")
def welcome_message() -> str:
    """A welcome message resource."""
    return "Welcome to the Basic MCP Server!"
