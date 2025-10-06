from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio
import os
from fastmcp.client.client import Client
from fastmcp.client.transports import StdioTransport

app = FastAPI()

# Models for API requests
class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict

class ResourceRequest(BaseModel):
    uri: str

# MCP client connection (reused across requests)
mcp_client = None

async def get_mcp_client():
    """Get or create MCP client connection"""
    global mcp_client
    if mcp_client is None:
        # Use fastmcp from PATH (works in production) or fallback to venv
        import shutil
        fastmcp_path = shutil.which("fastmcp") or "venv/bin/fastmcp"
        transport = StdioTransport(fastmcp_path, ["run", "basic_server.py"])
        mcp_client = Client(transport)
        await mcp_client.__aenter__()
    return mcp_client

@app.post("/api/call-tool")
async def call_tool(request: ToolCallRequest):
    """Call an MCP tool with the given arguments"""
    try:
        client = await get_mcp_client()
        result = await client.call_tool(request.tool_name, request.arguments)

        # Extract the actual content from the MCP response
        if hasattr(result, 'content') and len(result.content) > 0:
            content = result.content[0]
            if hasattr(content, 'text'):
                return {"result": content.text}

        return {"result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get-resource")
async def get_resource(request: ResourceRequest):
    """Get an MCP resource by URI"""
    try:
        client = await get_mcp_client()
        result = await client.read_resource(request.uri)

        # Extract the actual content from the MCP response
        if hasattr(result, 'contents') and len(result.contents) > 0:
            content = result.contents[0]
            if hasattr(content, 'text'):
                return {"result": content.text}

        return {"result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/list-tools")
async def list_tools():
    """List all available MCP tools"""
    try:
        client = await get_mcp_client()
        tools = await client.list_tools()
        return {"tools": [{"name": tool.name, "description": tool.description} for tool in tools]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve the HTML frontend
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    global mcp_client
    if mcp_client is not None:
        await mcp_client.__aexit__(None, None, None)
        mcp_client = None

# For running directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
