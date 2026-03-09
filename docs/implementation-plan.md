# Plan: AI Banking Assistant — Multi-Agent Architecture

## TL;DR
Build a banking personal assistant using a 3-tier architecture: mock REST APIs exposed via FastMCP (backend), Foundry Agent Service with supervisor + specialist agents (middle), and a React chat UI (frontend). Use Azure Developer CLI for provisioning/deployment in every phase. Agents are created as named persistent Foundry agents — on startup, look up by name and reuse if they already exist, otherwise create them. Streaming responses via Foundry Agent Service. No authentication initially.

---

## Phase 1: Project Scaffolding, Infra & Backend Deployment

**Goal:** Set up project structure, provision Azure resources, build mock banking services with MCP tools, and deploy backend to Azure.

1. Initialize project directory structure:
   - `backend/` — FastAPI app with mock REST APIs + FastMCP server
   - `middle/` — FastAPI app with Foundry Agent Service agents
   - `frontend/` — React chat UI app
   - `infra/` — Bicep templates for Azure resources
   - `azure.yaml` — Azure Developer CLI configuration
2. Create `infra/main.bicep` with Foundry account, project, model deployment (per requirements Bicep snippet); add Azure Container Registry and Container Apps for hosting backend and middle tier.
3. Create `azure.yaml` for `azd` provisioning and deployment hooks.
4. Add `requirements.txt` / `pyproject.toml` for backend Python dependencies (`fastapi`, `uvicorn`, `fastmcp`).
5. Add Dockerfile for backend (multi-arch aware per ARM requirement).
6. Create mock data layer (in-memory or JSON) with sample accounts, transactions, and payment methods.
7. Implement Account Service REST endpoints:
   - `GET /accounts/{id}` — account info
   - `GET /accounts/{id}/balance` — credit balance
   - `GET /accounts/{id}/payment-methods` — registered payment methods
8. Implement Transactions Service REST endpoints:
   - `GET /transactions?query=...` — search transactions
   - `GET /transactions?recipient=...` — filter by recipient
9. Implement Payments Service REST endpoint:
   - `POST /payments` — submit a payment
10. Embed FastMCP server in the FastAPI app, wrapping each service as an MCP tool:
    - `get_account_info`, `get_credit_balance`, `get_payment_methods`
    - `search_transactions`, `get_transactions_by_recipient`
    - `submit_payment`
11. Run `azd provision` to create Azure resources.
12. Deploy backend to Azure Container Apps via `azd deploy`.

**Verification:**
- Local: REST endpoints return correct mock data via Swagger UI; MCP tools are discoverable and callable.
- Azure: `azd deploy` succeeds; deployed backend responds to REST and MCP requests from Azure URL.

---

## Phase 2: Middle Tier — Single Agent End-to-End (Account Agent)

**Goal:** Stand up Foundry Agent Service with one specialist agent + supervisor, using streaming responses. Deploy to Azure and verify end-to-end in cloud.

*Depends on Phase 1 (backend must be deployed to Azure).*

13. Add `requirements.txt` for middle tier (`fastapi`, `uvicorn`, `azure-ai-projects`, `azure-identity`).
14. Add Dockerfile for middle tier.
15. Create FastAPI app for the middle tier with a `/chat` streaming endpoint (SSE) accepting user messages and streaming agent responses.
16. Initialize `AIProjectClient` using `DefaultAzureCredential` and Foundry endpoint (from env config).
17. Implement **named persistent agent management**: on startup, list existing agents and look up by name. If an agent with the target name exists, reuse it; otherwise create it. Apply to all agents.
18. Create the **Account Agent** (named `"account-agent"`) with MCP tool definition pointing to the deployed backend MCP server URL.
19. Create the **Supervisor Agent** (named `"supervisor-agent"`) with instructions to triage user requests; initially only routes to Account Agent.
20. Implement thread/conversation management — create threads, run agents with streaming via `project_client.agents.runs.stream()`, and send SSE events back to the client through the `/chat` endpoint.
21. Deploy middle tier to Azure Container Apps via `azd deploy`.

**Verification:**
- Local: `/chat` endpoint streams correct response for "What is my account balance?" via Supervisor → Account Agent → MCP tool → mock data.
- Azure: Same test against deployed Azure URL; streaming response arrives correctly.

---

## Phase 3: Frontend Tier — React Chat UI with Streaming

**Goal:** Build a conversational chat interface with streaming support, deploy to Azure.

*Depends on Phase 2 (middle tier must be deployed).*

22. Scaffold React app (Vite). Add `package.json` dependencies.
23. Build chat UI components: message list, input box, send button, streaming text indicator.
24. Implement SSE/streaming API integration with middle tier `/chat` endpoint — render tokens as they arrive.
25. Add conversation state management (message history, thread ID).
26. Style the UI for a clean banking assistant look.
27. Add CORS configuration on middle tier for frontend origin.
28. Add Dockerfile for frontend (or configure Azure Static Web Apps).
29. Deploy frontend to Azure Static Web Apps or Container Apps via `azd deploy`.

**Verification:**
- Local: User types a question, sees streamed response render progressively.
- Azure: Same behavior at deployed URL; frontend → middle tier → backend pipeline works in cloud.

---

## Phase 4: Add Remaining Agents (Transaction & Payments)

**Goal:** Extend the multi-agent system with remaining specialist agents. Deploy and verify in Azure.

*Depends on Phase 2.*

30. Create **Transaction Agent** (named `"transaction-agent"`) with MCP tool definition for transaction services — using the persistent agent pattern (reuse if exists).
31. Create **Payments Agent** (named `"payments-agent"`) with MCP tool definition for payment services — using the persistent agent pattern.
32. Update **Supervisor Agent** instructions to triage across all three agents based on user intent — update the existing named agent definition.
33. Deploy updated middle tier to Azure via `azd deploy`.

**Verification:**
- Local integration tests:
  - "Show me transactions with John" → Transaction Agent → correct results
  - "Pay $50 to Jane" → Payments Agent → payment submitted
  - "What's my balance?" → Account Agent → correct balance
- Azure: Same tests against deployed URL; all three agent paths work end-to-end with streaming.

---

## Phase 5: Integration Testing, Polish & Final Deployment

**Goal:** End-to-end validation, error handling, and production-ready deployment.

34. Full end-to-end tests: frontend → middle tier → backend across all three agent paths, both locally and in Azure.
35. Error handling: graceful failures for invalid requests, agent timeouts, MCP tool errors — surface errors cleanly in the streaming response and chat UI.
36. Environment variable configuration (`.env.sample` with all required vars documented).
37. Final `azd deploy` of all tiers.

**Verification:**
- All integration tests pass locally and against Azure deployment.
- UI handles errors gracefully (network failures, agent errors).
- Chat UI at deployed Azure URL communicates through the full pipeline with streaming.

---

## Relevant Files (to be created)

- `backend/app/main.py` — FastAPI app with REST endpoints + FastMCP server
- `backend/app/models.py` — Data models for accounts, transactions, payments
- `backend/app/mock_data.py` — In-memory mock data
- `backend/app/services/` — Account, Transaction, Payment service modules
- `backend/app/mcp_tools.py` — FastMCP tool definitions wrapping services
- `backend/Dockerfile` — Backend container image
- `backend/requirements.txt` — Python dependencies
- `middle/app/main.py` — FastAPI chat API with SSE streaming endpoint
- `middle/app/agents.py` — Named persistent agent management (create-or-reuse pattern), streaming runs
- `middle/app/config.py` — Environment/config management
- `middle/Dockerfile` — Middle tier container image
- `middle/requirements.txt` — Python dependencies
- `frontend/src/App.tsx` — React app entry
- `frontend/src/components/Chat.tsx` — Chat UI with streaming text rendering
- `frontend/src/services/api.ts` — SSE/streaming API client for middle tier
- `frontend/package.json` — Node dependencies
- `frontend/Dockerfile` — Frontend container image
- `infra/main.bicep` — Azure resource definitions (Foundry, model, ACR, Container Apps, Static Web Apps)
- `infra/main.parameters.json` — Bicep parameters
- `azure.yaml` — Azure Developer CLI project config (all three services)

## Decisions

- **No MAF**: Per requirements, use Foundry Agent Service directly (not Microsoft Agent Framework).
- **Incremental delivery**: Phase 2 delivers one working agent end-to-end before Phase 4 adds the rest.
- **Named persistent agents**: Agents are created with fixed names (e.g., `"account-agent"`). On startup, look up by name — reuse if exists, create if not.
- **Streaming**: Use Foundry Agent Service streaming (`project_client.agents.runs.stream()`) with SSE to the frontend.
- **No authentication initially**: Auth deferred to a future phase.
- **Deploy every phase**: Each phase includes `azd deploy` and Azure-side functional testing.
- **FastMCP embedded in FastAPI**: Single backend app serves both REST and MCP endpoints.
- **Mock data**: In-memory/JSON — no database needed for this demo.
- **Multi-arch Docker builds**: Required for local ARM dev machines deploying to Linux Azure hosts.

## Further Considerations

1. **Conversation persistence:** Currently threads are in-memory in the middle tier. Foundry manages thread state server-side — consider exposing thread resumption in a future phase.
2. **Authentication (future):** Add API key or Azure AD for the chat API once core functionality is proven.
