# Creating and Managing Agents in Flotorch

## Overview

Agents in Flotorch are intelligent systems that can interact with users, use tools, and make decisions based on LLM capabilities. Flotorch ADK (Agent Development Kit) provides a framework for building powerful agents.

## Creating Agents

### Step 1: Define Agent Configuration

Agents are created through the Flotorch Console or programmatically using the SDK. Each agent has:
- **Agent Name**: Unique identifier for your agent
- **Model Configuration**: Which LLM model to use
- **Tools**: Custom functions the agent can call
- **System Instructions**: Behavior and personality guidelines

### Step 2: Using Flotorch ADK Agent

```python
from flotorch.adk.agent import FlotorchADKAgent

agent_client = FlotorchADKAgent(
    agent_name="my-agent",
    base_url=FLOTORCH_BASE_URL,
    api_key=FLOTORCH_API_KEY
)
agent = agent_client.get_agent()
```

### Step 3: Adding Custom Tools

Agents can use custom tools to extend their capabilities:

```python
from google.adk.tools import FunctionTool

def my_custom_tool(input: str) -> str:
    """Tool description for the LLM"""
    # Tool implementation
    return result

tools = [FunctionTool(my_custom_tool)]
agent_client = FlotorchADKAgent(
    agent_name="my-agent",
    custom_tools=tools,
    ...
)
```

## Agent Sessions

Sessions manage conversation context and history:

```python
from flotorch.adk.sessions import FlotorchADKSession

session_service = FlotorchADKSession(
    api_key=FLOTORCH_API_KEY,
    base_url=FLOTORCH_BASE_URL
)

session = await session_service.create_session(
    app_name="my-app",
    user_id="user-123"
)
```

## Running Agents

Use the Google ADK Runner to execute agent queries:

```python
from google.adk.runners import Runner
from google.genai import types

runner = Runner(
    agent=agent,
    app_name="my-app",
    session_service=session_service
)

content = types.Content(role="user", parts=[types.Part(text="Hello!")])
events = runner.run(user_id="user-123", session_id=session.id, new_message=content)
```

## Best Practices

1. **Clear Tool Descriptions**: Provide detailed docstrings for tools
2. **Error Handling**: Implement robust error handling in tools
3. **Session Management**: Properly manage session lifecycle
4. **Observability**: Enable tracing for debugging and monitoring

