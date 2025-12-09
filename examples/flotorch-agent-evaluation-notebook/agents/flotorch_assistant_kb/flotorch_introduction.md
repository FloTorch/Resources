# Flotorch Introduction

## What is Flotorch?

Flotorch is a comprehensive platform for building, deploying, and managing AI agents and applications. It provides a unified gateway for accessing various LLM providers, managing knowledge bases, and orchestrating agent workflows.

## Key Features

### 1. Unified LLM Gateway
- Access multiple LLM providers through a single API
- Consistent interface across different models
- Built-in rate limiting and cost tracking

### 2. Agent Development Kit (ADK)
- Build agents using Google ADK framework
- Support for multi-turn conversations
- Built-in session management
- Tool integration capabilities

### 3. Knowledge Base & RAG
- Create and manage vector stores
- Semantic search capabilities
- Retrieval-Augmented Generation (RAG) support
- Easy integration with agents

### 4. Observability & Tracing
- OpenTelemetry integration
- Detailed execution traces
- Performance monitoring
- Cost tracking

## Getting Started

To get started with Flotorch:

1. Sign up for a Flotorch account
2. Obtain your API key from the Console
3. Install the Flotorch SDK: `pip install flotorch`
4. Configure your gateway URL and API key
5. Start building agents!

## Architecture

Flotorch follows a microservices architecture:
- **Gateway**: Routes requests to appropriate services
- **Agent Service**: Manages agent lifecycle and execution
- **Memory Service**: Handles knowledge bases and vector stores
- **Observability Service**: Tracks traces and metrics

