import asyncio
from typing import Dict, Any, Optional
from openai import OpenAI
from src.mcp_server.server import mcp_server
import json
import requests


class AIAgentService:
    def __init__(self, openrouter_api_key: str = None):
        """Initialize the AI Agent service with OpenRouter API key."""
        # Configure OpenAI client for OpenRouter, but only if API key exists
        if openrouter_api_key and openrouter_api_key.strip():
            try:
                self.client = OpenAI(
                    api_key=openrouter_api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            except Exception:
                # If OpenAI client initialization fails, we can still use the simulation approach
                self.client = None
        else:
            # No API key provided, only use simulation approach
            self.client = None

        self.mcp_server = mcp_server
        # Hardcode the backend URL
        self.mcp_server_url = "https://muhammedsuhaib-raheel.hf.space"

    def initialize_agent_with_tools(self):
        """
        Initialize the OpenAI agent with the available MCP tools.
        """
        # Get the list of available tools from the MCP server
        self.available_tools = list(self.mcp_server.tools.keys())

        # Create tool definitions for OpenAI
        self.openai_tools = []
        for tool_name in self.available_tools:
            # Create a basic tool definition - in a real implementation,
            # we would have more detailed function definitions
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": f"Tool to perform {tool_name.replace('_', ' ')} operation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user performing the action"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            }

            # Add specific parameters based on the tool
            if tool_name == "add_task":
                tool_def["function"]["parameters"]["properties"].update({
                    "title": {"type": "string", "description": "The title of the task to add"},
                    "description": {"type": "string", "description": "Optional description of the task"},
                    "priority": {"type": "string", "description": "Priority level (low, medium, high)"}
                })
                tool_def["function"]["parameters"]["required"].extend(["title"])

            elif tool_name == "list_tasks":
                # list_tasks only needs user_id which is already included
                pass

            elif tool_name == "complete_task":
                tool_def["function"]["parameters"]["properties"]["task_id"] = {
                    "type": "string",
                    "description": "The ID of the task to mark as complete"
                }
                tool_def["function"]["parameters"]["required"].append("task_id")

            elif tool_name == "update_task":
                tool_def["function"]["parameters"]["properties"].update({
                    "task_id": {"type": "string", "description": "The ID of the task to update"},
                    "title": {"type": "string", "description": "New title for the task (optional)"},
                    "description": {"type": "string", "description": "New description for the task (optional)"},
                    "priority": {"type": "string", "description": "New priority for the task (optional)"},
                    "completed": {"type": "boolean", "description": "New completion status for the task (optional)"}
                })
                tool_def["function"]["parameters"]["required"].append("task_id")

            elif tool_name == "delete_task":
                tool_def["function"]["parameters"]["properties"]["task_id"] = {
                    "type": "string",
                    "description": "The ID of the task to delete"
                }
                tool_def["function"]["parameters"]["required"].append("task_id")

            self.openai_tools.append(tool_def)

        return self

    async def process_user_input(self, user_input: str, conversation_history: list = None) -> Dict[str, Any]:
        """
        Process user input through the AI agent and return the response.

        Args:
            user_input: Natural language input from the user
            conversation_history: Previous conversation history for context

        Returns:
            Dictionary containing the AI response and any tool calls made
        """
        # If we have a client (OpenRouter is properly configured), use it
        if self.client:
            # Prepare the messages for the AI
            messages = []
            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": user_input})

            try:
                # Call OpenRouter API with tools
                response = self.client.chat.completions.create(
                    model="openai/gpt-oss-120b:free",  # Using the specified OpenRouter free model
                    messages=messages,
                    tools=self.openai_tools,
                    tool_choice="auto",
                    max_tokens=1000,
                    temperature=0.7
                )

                # Process the response
                choice = response.choices[0]

                # Initialize return values
                response_text = choice.message.content if choice.message.content else "I processed your request."
                tool_calls = []

                if choice.message.tool_calls:
                    for tool_call in choice.message.tool_calls:
                        tool_calls.append({
                            "name": tool_call.function.name,
                            "arguments": json.loads(tool_call.function.arguments)
                        })

                return {
                    "response": response_text,
                    "tool_calls": tool_calls,
                    "tool_responses": []
                }
            except Exception as e:
                # If OpenRouter call fails, fall back to simulation
                print(f"OpenRouter API call failed: {str(e)}. Falling back to simulation.")

        # Fallback to simulation if OpenRouter is not configured or fails
        # Prepare the messages for the AI
        messages = []
        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": user_input})

        # Simple keyword matching to simulate AI understanding
        if "add" in user_input.lower() and ("task" in user_input.lower() or "buy" in user_input.lower()):
            # Simulate AI recognizing an add_task command
            title = user_input.split("add a task to ")[-1] if "add a task to " in user_input.lower() else user_input.split("to ")[-1]

            return {
                "response": f"I'll add a task for you: {title}",
                "tool_calls": [{
                    "name": "add_task",
                    "arguments": {
                        "title": title
                    }
                }],
                "tool_responses": []
            }

        elif "show" in user_input.lower() or "list" in user_input.lower():
            # Simulate AI recognizing a list_tasks command
            return {
                "response": "I'll show you your tasks",
                "tool_calls": [{
                    "name": "list_tasks",
                    "arguments": {}
                }],
                "tool_responses": []
            }

        elif "complete" in user_input.lower() or "mark" in user_input.lower():
            # Simulate AI recognizing a complete_task command
            # Extract task ID from input (simple approach)
            import re
            task_ids = re.findall(r'\d+', user_input)
            if task_ids:
                task_id = task_ids[0]
                return {
                    "response": f"I'll mark task {task_id} as complete",
                    "tool_calls": [{
                        "name": "complete_task",
                        "arguments": {
                            "task_id": task_id
                        }
                    }],
                    "tool_responses": []
                }

        # For other inputs, return a default response
        return {
            "response": f"I received your message: '{user_input}'. This is a placeholder response.",
            "tool_calls": [],
            "tool_responses": []
        }

    def execute_tool_call(self, tool_name: str, tool_arguments: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute an MCP tool call.

        Args:
            tool_name: Name of the tool to call
            tool_arguments: Arguments for the tool
            user_id: ID of the authenticated user

        Returns:
            Result of the tool execution
        """
        # Add user_id to arguments to ensure proper scoping
        tool_arguments['user_id'] = user_id

        # Make a request to the MCP server to execute the tool
        try:
            # Add timeout to prevent hanging requests
            response = requests.post(
                f"{self.mcp_server_url}/execute",
                json={
                    "name": tool_name,
                    "arguments": tool_arguments
                },
                timeout=30  # 30 second timeout
            )

            if response.status_code == 200:
                result = response.json()

                # The MCP server returns a response in the format:
                # {"success": true/false, "result": actual_tool_result, "error": error_message}
                # Check if the MCP server call itself failed
                if isinstance(result, dict) and result.get("success") is False:
                    error_msg = result.get('error', 'Unknown error from MCP server')
                    return {
                        "error": f"MCP server error: {error_msg}",
                        "details": result
                    }

                # If MCP server call succeeded, return the actual tool result (in the "result" field)
                # The actual tool execution result is in result["result"]
                tool_execution_result = result.get("result", {})

                # Check if the actual tool execution failed
                if isinstance(tool_execution_result, dict) and tool_execution_result.get("success") is False:
                    error_msg = tool_execution_result.get('error', 'Unknown error from tool execution')
                    return {
                        "error": f"Tool execution failed: {error_msg}",
                        "details": tool_execution_result
                    }

                return tool_execution_result
            else:
                return {
                    "error": f"Tool execution failed with status {response.status_code}",
                    "details": response.text
                }
        except requests.exceptions.ConnectionError:
            return {
                "error": f"Cannot connect to MCP server at {self.mcp_server_url}. Please ensure the MCP server is running.",
                "details": "Connection error"
            }
        except requests.exceptions.Timeout:
            return {
                "error": "Tool execution timed out. The MCP server may be busy or unresponsive.",
                "details": "Timeout error"
            }
        except Exception as e:
            return {
                "error": f"Failed to execute tool: {str(e)}",
                "details": str(type(e).__name__)
            }

    async def process_natural_language_request(
        self,
        user_input: str,
        user_id: str,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a complete natural language request from a user.

        Args:
            user_input: Natural language command from the user
            user_id: ID of the authenticated user
            conversation_id: Optional conversation ID for context

        Returns:
            Dictionary with the final response and execution details
        """
        # Get conversation history if available
        conversation_history = []
        if conversation_id:
            # In a real implementation, we'd fetch the conversation history
            pass

        try:
            # Process the user input with the AI agent
            result = await self.process_user_input(user_input, conversation_history)

            # Execute any tool calls that the AI agent selected
            if result.get('tool_calls'):
                for tool_call in result['tool_calls']:
                    tool_result = self.execute_tool_call(
                        tool_call['name'],
                        tool_call['arguments'],
                        user_id
                    )

                    # Add tool result to the response
                    if 'tool_results' not in result:
                        result['tool_results'] = []
                    result['tool_results'].append(tool_result)

                    # If there was an error in tool execution, include it in the response
                    if isinstance(tool_result, dict) and 'error' in tool_result:
                        # Return a user-friendly error message
                        return {
                            "response": f"Sorry, I encountered an error processing your request: {tool_result['error']}. Please try again.",
                            "tool_calls": result.get('tool_calls', []),
                            "tool_results": result.get('tool_results', []),
                            "error_occurred": True
                        }

            return result
        except Exception as e:
            # Handle any unexpected errors in the process
            return {
                "response": "Sorry, I encountered an error processing your request. Please try again.",
                "error": str(e),
                "error_occurred": True
            }