from fastapi import APIRouter, Request
from copilotkit.integrations.fastapi import CopilotKitSDK
from backend.unified_agent_orchestrator_v76 import TrinitySwarm
import os

router = APIRouter()

# Initialize the Trinity Swarm (main agent system)
swarm = TrinitySwarm()

# CopilotKit SDK — connects the Trinity Swarm agents to the frontend chat
sdk = CopilotKitSDK(
    agents=[],
    commands={}
)


@router.post("/copilot/chat")
async def chat(request: Request):
    return await sdk.handle_request(request)
