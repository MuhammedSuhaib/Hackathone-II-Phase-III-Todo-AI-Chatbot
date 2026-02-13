"""
Script to start the MCP server for the Todo AI Chatbot
"""
from src.mcp_server.server import mcp_server
from register_mcp_tools import register_all_tools

if __name__ == "__main__":
    print("Starting MCP Server for Todo AI Chatbot...")
    register_all_tools()
    print(f"Available tools: {list(mcp_server.tools.keys())}")
    print("MCP Server will run on https://muhammedsuhaib-raheel.hf.space")
    # Use environment-provided port for Hugging Face Spaces, default to 8001
    port = int(os.getenv("PORT", 8001))
    mcp_server.start(host="0.0.0.0", port=port)