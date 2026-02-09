from fastapi import APIRouter, Request
from copilotkit.integrations.fastapi import CopilotKitSDK
from copilotkit import CopilotKit
from backend.unified_agent_orchestrator_v76 import TrinitySwarm
import os

router = APIRouter()

# Initialize the Trinity Swarm (your main agent system)
swarm = TrinitySwarm()

# Define a simple LangChain-style or direct handler if CopilotKit SDK allows
# For now, we use the standard SDK setup
sdk = CopilotKitSDK(
    agents=[
        # we can define agents here if we want them exposed to the frontend
        # For now, we will just expose a basic chat that can talk to Trinity
    ],
    commands={}
)


@router.post("/copilot/chat")
async def chat(request: Request):
    return await sdk.handle_request(request)
