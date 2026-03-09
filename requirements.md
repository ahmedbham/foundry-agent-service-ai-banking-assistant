# Objective

A banking personal assistant AI chat application to allow users to interact with their bank account information, transaction history, and payment functionalities. Utilizing the power of generative AI within a multi-agent architecture, this assistant aims to provide a seamless, conversational interface through which users can effortlessly access and manage their financial data.

---

## Functional Architecture

### Backend Tier

**Backend Banking Services**

- **Account Service:** Support following functionality: banking account information, credit balance, and registered payment methods.
- **Transactions Service:** Enables searching transactions and retrieving transactions by recipient.
- **Payments Service:** To submit payments.

### Middle Tier

An AI chat API that allows frontend chat application to prompt using natural language and invoke appropriate backend banking services based on user intent.

### Frontend Tier

A chat UI that allows users to interact with their bank account information, transaction history, and payment functionalities.

---

## Technical Architecture

### Backend Tier

- Mock REST APIs that expose appropriate operations/methods
- **MCP Server**: FastMCP embedded in the FastAPI app, exposing banking tools for agents to consume
- Using any hosting solution (e.g., Azure Logic Apps, Azure App Service, Azure Functions Apps, etc.) for MCP Server, which can be called by the AI agents in the middle tier

### Middle Tier

- Using Foundry Agent Service (from Microsoft Foundry SDK v2) for agent runtime, orchestration and management
- **Account Agent** that uses Account Services MCP tool
- **Transaction Agent** that uses Transaction Services MCP tool
- **Payments Agent** that uses Payments Services MCP tool
- **Supervisor Agent:** To triage the user request, and use the appropriate agent to handle the request, and also to handle the conversation flow

### Frontend Tier

A react-based chat UI that allows users to ask banking questions and receive responses from the backend services through the AI agents. The UI will be designed to provide a seamless and intuitive user experience, allowing users to easily access their account information, transaction history, and payment functionalities. The chat interface will support natural language processing to understand user queries and provide accurate responses based on the data retrieved from the backend services.

---
## Non-Functional Requirements
### Implementation Phases

Follow an incremental delivery pattern. Implement and test end to end with a single agent before adding additional agents.

### Technical Requirements
- Do not use Microsoft Agent Framework (MAF) for this implementation. The goal is to demonstrate the use of Foundry Agent Service for agent runtime, orchestration and management.
- to Create a project client using Microsoft Foundry SDK v2 to interact with the Foundry Agent Service and manage the agents:
```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

project_client = AIProjectClient(
  endpoint="https://<resource-name>.services.ai.azure.com/api/projects/<project-name>",
  credential=DefaultAzureCredential())
```
- to Create an OpenAI-compatible client from your project:
```python
with project_client.get_openai_client() as openai_client:
    response = openai_client.responses.create(
        model="gpt-5.2",
        input="What is the size of France in square miles?",
    )
    print(f"Response output: {response.output_text}")
```
- sample code to create and run an agent:
```python
agent = project_client.agents.create_agent(
        model=os.getenv("MODEL_DEPLOYMENT_NAME"),  # Model deployment name
        name="my-agent",  # Name of the agent
        instructions="""You politely help with math questions. 
        Use the Code Interpreter tool when asked to visualize numbers.""",  
        # Instructions for the agent
        tools=code_interpreter.definitions,  # Attach the tool
        tool_resources=code_interpreter.resources,  # Attach tool resources
    )
run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id,
        additional_instructions="""Please address the user as Jane Doe.
        The user has a premium account.""",
    )  
```
- an alternative way to create and run an agent using the OpenAI-compatible client:
```python
 Create a prompt agent with MCP tool capabilities
agent = project.agents.create_version(
    agent_name="MyAgent7",
    definition=PromptAgentDefinition(
        model="gpt-5-mini",
        instructions="Use MCP tools as needed",
        tools=[tool],
    ),
)
```
- to create a tool definition for MCP Server APIs:
```python
tool = MCPTool(
    server_label="api-specs",
    server_url="https://api.githubcopilot.com/mcp",
    require_approval="always",
    project_connection_id=MCP_CONNECTION_NAME,
)
```
- Foundry & Model Deployment — Bicep

```bicep
resource foundry 'Microsoft.CognitiveServices/accounts@2025-10-01-preview' = {
    name: foundryAccountName
    location: location
    kind: 'AIServices'
    identity: { type: 'SystemAssigned' }
    sku: { name: 'S0' }
    properties: {
        customSubDomainName: foundryAccountName
        publicNetworkAccess: 'Enabled'
        allowProjectManagement: true
    }

    resource project 'projects' = {
        name: foundryProjectName
        location: location
        identity: { type: 'SystemAssigned' }
        properties: {}
    }

    resource model 'deployments' = {
        name: 'agent-model'
        sku: {
            capacity: 10
            name: 'GlobalStandard'
        }
        properties: {
            model: {
                format: 'OpenAI'
                name: 'gpt-4.1'
                version: '2025-04-14'
            }
            raiPolicyName: 'Microsoft.DefaultV2'
        }
    }
}
```
- Use Azure Developer CLI for Azure resource provisioning and deployment.
- any local build will create ARM based architecture. For deployment to Azure on linux hosts, build docker images remotely using Azure Container Registry Tasks or use multi-arch builds with Docker Buildx.
