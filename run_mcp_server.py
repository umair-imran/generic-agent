from mcp_server import booking_server

if __name__ == "__main__":
    print("Starting MCP server...")
    booking_server.mcp.run(transport="sse")
    print("MCP server is running")