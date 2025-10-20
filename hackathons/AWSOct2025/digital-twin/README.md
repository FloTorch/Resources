# Digital Twin Knowledge Base System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![AWS](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock)
[![FloTorch](https://img.shields.io/badge/FloTorch-Agent-green.svg)](https://flotorch.cloud)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

The Digital Twin Knowledge Base System is a comprehensive application designed to create intelligent digital representations of companies through advanced knowledge management and AI-powered interactions. The system enables users to query and interact with detailed company information through a conversational interface powered by FloTorch agents and AWS Bedrock knowledge bases.

## Key Features

- **Multi-Company Knowledge Base**: Supports multiple companies across different industries
- **AI-Powered Interactions**: Intelligent responses using FloTorch agents and AWS Bedrock
- **Comprehensive Data Management**: Detailed company profiles with extensive information
- **Industry-Specific Insights**: Tailored responses based on company industry and context
- **Scalable Architecture**: Built with modern technologies for performance and reliability

## Technology Stack

### Backend Technologies
- **Python 3.8+**: Core application language
- **Streamlit**: Web application framework for user interface
- **AWS Bedrock**: Knowledge base and AI services
- **FloTorch**: Agent orchestration and workflow management
- **Pydantic**: Data validation and settings management

### AI and Machine Learning
- **AWS Bedrock Knowledge Bases**: Vector database and retrieval system
- **FloTorch Gateway**: Agent creation, management, and API gateway
- **Strands Framework**: Agent building framework for intelligent workflows
- **Natural Language Processing**: Query understanding and response generation

### Data Management
- **Structured Data Storage**: Company information in organized text formats
- **Vector Embeddings**: Semantic search and retrieval capabilities
- **Knowledge Base Integration**: Seamless data ingestion and querying

## Project Structure

The project is organized into several key components:

- **src/digital_twin/**: Core application source code
  - **core/**: Configuration and service management
  - **agents/**: Agent orchestration and management
  - **knowledge/**: Knowledge base operations
  - **ui/**: User interface components

- **digital_twin/**: Company data storage
  - **amazon/**: Amazon company information
  - **walmart/**: Walmart company information
  - **fissionlabs/**: Fission Labs company information
  - **aws/**: AWS company information

## Prerequisites

Before running the application, ensure you have the following:

1. **Python 3.8 or higher**
2. **FloTorch Account** and console access
3. **Required Python packages** (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/venkateswarlu-garnimitta/digital-twin.git
cd digital_twin
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Knowledge Base Configuration (Configure in FloTorch Console)
# Get these IDs from your FloTorch console knowledge base setup
# FloTorch Configuration (Get these from FloTorch Console)
FLOTORCH_API_KEY=your-flotorch-api-key
FLOTORCH_BASE_URL=your-flotorch-base-url
FLOTORCH_AGENT_NAME=your-agent-name
VECTOR_STORE_ID=your_flotorch_vectorstore_id
```

### Knowledge Base Setup

1. **Access FloTorch Console**: Navigate to https://console.flotorch.cloud/
2. **Configure Knowledge Base**:
   - Create or access your knowledge base in the FloTorch console
   - Upload company data files to your knowledge base
   - Configure data sources and indexing
3. **Update Environment Variables**: Add your FloTorch API key, base URL, agent name and vector store ID to the `.env` file

### FloTorch Agent Configuration

1. **Access FloTorch Console**: Navigate to https://console.flotorch.cloud/
2. **Create New Agent**:
   - Agent Name: `digital-twin`
   - Agent Goal: `Always provide SHORT, CONCISE answers to fit in a chat interface.`
   - System Prompt: 
   ```
   You are a helpful representative for the company.

   COMPANY CONTEXT:
   - You represent the company
   - The company operates in their respective industry
   - You have access to company information through the knowledge base

   IMPORTANT INSTRUCTIONS:
   - Always provide SHORT, CONCISE answers to fit in a chat interface.
   - Keep responses under 200 words
   - Use the knowledge base tool to get accurate information about the company
   - Give direct answers without unnecessary details
   - Be conversational and helpful
   - If you don't know something about the company, say so clearly
   - Always speak as a representative of the company

   Answer questions about the company using the knowledge base tool when needed
   ```

3. **Configure Agent Settings**: Set up appropriate permissions and access controls
4. **Test Agent**: Verify the agent responds correctly to sample queries

### Strands Framework Integration

The system leverages the **Strands Framework** for building intelligent agents with the following capabilities:

#### Agent Architecture
- **Strands Framework**: Core framework for agent development and workflow orchestration
- **FloTorch Gateway**: API gateway for agent creation, management, and invocation
- **Knowledge Base Integration**: Seamless connection between agents and AWS Bedrock knowledge bases
- **Workflow Automation**: Intelligent routing and processing of user queries

#### Agent Capabilities
- **Contextual Understanding**: Agents maintain conversation context and company-specific knowledge
- **Dynamic Response Generation**: Real-time responses based on knowledge base queries
- **Multi-turn Conversations**: Support for follow-up questions and extended dialogues
- **Error Handling**: Graceful handling of unknown queries and system errors

#### Development Workflow
1. **Agent Definition**: Define agent behavior and capabilities using Strands framework
2. **Knowledge Integration**: Connect agents to relevant company knowledge bases
3. **Testing & Validation**: Test agent responses and refine behavior
4. **Deployment**: Deploy agents through FloTorch gateway for production use

## Running the Application

1. **Start the Streamlit Application**:
```bash
streamlit run main.py
```

2. **Access the Application**: Open your browser and navigate to the provided local URL (typically http://localhost:8501)

3. **Select Company**: Choose from the available companies (Amazon, Walmart, Fission Labs, AWS)

4. **Start Querying**: Begin asking questions about the selected company

## Usage

### Basic Operations

1. **Company Selection**: Choose a company from the dropdown menu
2. **Query Input**: Enter your question in the chat interface
3. **Response Generation**: The system will provide concise, accurate answers based on the knowledge base
4. **Follow-up Questions**: Continue the conversation with additional queries

### Query Examples

- "What are the main services offered by this company?"
- "Who are the key executives and leadership team?"
- "What is the company's financial performance?"
- "What are the recent partnerships and acquisitions?"
- "How does the company approach innovation and technology?"

## Troubleshooting

### Common Issues

1. **Knowledge Base Connection Errors**:
   - Verify FloTorch console configuration
   - Check vector store ID in .env file
   - Ensure data is properly uploaded to FloTorch knowledge base

2. **FloTorch Agent Issues**:
   - Verify agent configuration in FloTorch console
   - Check API key and agent ID
   - Ensure agent has proper permissions

3. **Application Startup Problems**:
   - Verify all dependencies are installed
   - Check environment variables
   - Review application logs for specific errors

### Support

For technical support and troubleshooting:
1. Check the application logs for detailed error messages
2. Verify all configuration settings
3. Ensure all prerequisites are met
4. Review the FloTorch and AWS documentation

## Contributing

To contribute to this project:
1. Follow the established code structure and conventions
2. Ensure all new features are properly tested
3. Update documentation as needed
4. Submit pull requests with clear descriptions

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- AWS Bedrock for knowledge base services
- FloTorch for agent orchestration and gateway services
- Strands Framework for agent building and development
- Streamlit for the web interface
- All contributors and supporters of this project
