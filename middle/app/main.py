import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from .config import FOUNDRY_ENDPOINT, MODEL_DEPLOYMENT_NAME
from .agents import (
    ensure_account_agent,
    ensure_supervisor_agent,
    resolve_agent_for_message,
    get_tools_for_agent,
    get_instructions_for_agent,
)


project_client: AIProjectClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global project_client
    project_client = AIProjectClient(
        endpoint=FOUNDRY_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    # Ensure agents exist (create-or-reuse)
    ensure_account_agent(project_client)
    ensure_supervisor_agent(project_client)
    print("Agents ready")
    yield
    project_client.close()


app = FastAPI(title="Banking AI Chat API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


@app.post("/chat")
async def chat(request: ChatRequest):
    """Stream a chat response via SSE, routing to the appropriate agent."""
    agent_name = resolve_agent_for_message(request.message)
    tools = get_tools_for_agent(agent_name)
    instructions = get_instructions_for_agent(agent_name)

    def event_stream():
        openai_client = project_client.get_openai_client()
        with openai_client:
            create_kwargs = {
                "model": MODEL_DEPLOYMENT_NAME,
                "input": request.message,
                "instructions": instructions,
                "stream": True,
            }
            if tools:
                create_kwargs["tools"] = tools
            if request.conversation_id:
                create_kwargs["previous_response_id"] = request.conversation_id

            stream = openai_client.responses.create(**create_kwargs)

            response_id = None
            for event in stream:
                if event.type == "response.output_text.delta":
                    data = json.dumps({"type": "delta", "content": event.delta})
                    yield f"data: {data}\n\n"

                elif event.type == "response.completed":
                    response_id = event.response.id if hasattr(event, "response") else None
                    data = json.dumps({
                        "type": "done",
                        "conversation_id": response_id or "",
                    })
                    yield f"data: {data}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/health")
def health():
    return {"status": "healthy"}
