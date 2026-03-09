"""Named persistent agent management — create-or-reuse pattern with code-based routing."""

from azure.ai.projects import AIProjectClient, models
from azure.core.exceptions import ResourceNotFoundError

from .config import MODEL_DEPLOYMENT_NAME, BACKEND_MCP_URL

# Cache agent definitions for runtime use (agent_name → definition)
_agent_defs: dict[str, models.PromptAgentDefinition] = {}


def _build_mcp_tool(allowed_tools: list[str]) -> models.MCPTool:
    """Build an MCP tool definition pointing to the backend."""
    return models.MCPTool(
        server_label="banking-backend",
        server_url=BACKEND_MCP_URL,
        require_approval="never",
        allowed_tools=allowed_tools,
    )


def get_or_create_agent(
    client: AIProjectClient,
    agent_name: str,
    definition: models.AgentDefinition,
    description: str = "",
) -> None:
    """Ensure an agent exists by name; create it if not found."""
    try:
        client.agents.get(agent_name)
        print(f"Reusing agent '{agent_name}'")
    except ResourceNotFoundError:
        print(f"Creating agent '{agent_name}'")
        client.agents.create_version(
            agent_name=agent_name,
            definition=definition,
            description=description,
        )


def ensure_account_agent(client: AIProjectClient) -> None:
    """Create or reuse the Account Agent with MCP tool for banking services."""
    mcp_tool = _build_mcp_tool(
        ["get_account_info", "get_credit_balance", "get_payment_methods"]
    )

    definition = models.PromptAgentDefinition(
        model=MODEL_DEPLOYMENT_NAME,
        instructions=(
            "You are the Account Agent for a banking assistant. "
            "You help users with account information, credit balances, and payment methods. "
            "Use the MCP tools to retrieve data from the banking backend. "
            "Always use account_id 'ACC001' unless the user specifies otherwise. "
            "Present information clearly and concisely."
        ),
        tools=[mcp_tool],
    )

    _agent_defs["account-agent"] = definition
    get_or_create_agent(
        client, "account-agent", definition, "Handles account info, balances, payment methods"
    )


def ensure_supervisor_agent(client: AIProjectClient) -> None:
    """Create or reuse the Supervisor Agent for general/unknown queries."""
    definition = models.PromptAgentDefinition(
        model=MODEL_DEPLOYMENT_NAME,
        instructions=(
            "You are the Supervisor Agent for a banking assistant. "
            "You handle general questions and help the user understand what "
            "services are available. You can help with: account information, "
            "credit balances, and payment methods. "
            "If the user asks about something outside these areas, let them "
            "know what you can help with."
        ),
    )

    _agent_defs["supervisor-agent"] = definition
    get_or_create_agent(
        client, "supervisor-agent", definition, "Handles general queries and unknown intents"
    )


# Routing keywords for each specialist agent
_ROUTING_RULES = {
    "account-agent": [
        "account", "balance", "credit", "payment method", "payment methods",
        "card", "cards", "debit", "checking", "savings",
    ],
}


def resolve_agent_for_message(message: str) -> str:
    """Route a user message to the appropriate agent based on keywords."""
    lower = message.lower()
    for agent_name, keywords in _ROUTING_RULES.items():
        if any(kw in lower for kw in keywords):
            return agent_name
    return "supervisor-agent"


def get_tools_for_agent(agent_name: str) -> list[dict]:
    """Return the MCP tool definitions for the given agent as dicts for responses API."""
    definition = _agent_defs.get(agent_name)
    if not definition or not definition.tools:
        return []
    tools = []
    for tool in definition.tools:
        if isinstance(tool, models.MCPTool):
            tool_dict = {
                "type": "mcp",
                "server_label": tool.server_label,
                "server_url": tool.server_url,
                "require_approval": tool.require_approval,
            }
            if tool.allowed_tools:
                tool_dict["allowed_tools"] = tool.allowed_tools
            tools.append(tool_dict)
    return tools


def get_instructions_for_agent(agent_name: str) -> str:
    """Return the instructions for the given agent."""
    definition = _agent_defs.get(agent_name)
    return definition.instructions if definition else ""
