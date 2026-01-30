# Using the Flotorch Console

## Overview

The Flotorch Console is a web-based interface for managing your Flotorch resources including agents, knowledge bases, models, and API keys.

## Key Features

### 1. Dashboard
- Overview of your account usage
- Cost tracking and analytics
- Recent activity monitoring

### 2. Agents Management
- Create and configure agents
- Test agents interactively
- View agent execution history
- Manage agent settings and tools

### 3. Knowledge Bases
- Create and manage vector stores
- Upload documentation files
- Configure embedding models
- Test semantic search

### 4. Models & Providers
- View available LLM models
- Configure model access
- Set up provider credentials
- Monitor model usage

### 5. API Keys
- Generate and manage API keys
- Set up rate limits
- Configure access permissions
- View usage statistics

## Creating a Knowledge Base

1. Navigate to **Knowledge Bases** in the Console
2. Click **Create New Knowledge Base**
3. Enter a name and description
4. Upload documentation files (supports .md, .txt, .pdf)
5. Configure embedding settings
6. Wait for indexing to complete
7. Copy the Knowledge Base ID for use in your code

## Creating an Agent

1. Go to **Agents** section
2. Click **Create Agent**
3. Provide agent name and description
4. Select the LLM model
5. Configure system instructions
6. Add custom tools (optional)
7. Save and test the agent

## Viewing Traces

1. Navigate to **Observability** section
2. View execution traces for agents
3. Analyze latency and performance
4. Review token usage and costs
5. Debug agent execution issues

## API Integration

All Console operations can also be performed via the Flotorch SDK or REST API. The Console provides a user-friendly interface, while the API enables programmatic management.

## Security

- Keep your API keys secure
- Use environment variables for sensitive data
- Regularly rotate API keys
- Monitor for unauthorized access

