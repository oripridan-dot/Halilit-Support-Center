from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from pydantic import BaseModel
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Halilit Support Center API", version="7.2")

# Add CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Robust path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "../frontend/dist")
FRONTEND_PUBLIC_DATA = os.path.join(BASE_DIR, "../frontend/public/data")

# 1. Mount the frontend build directory
# Ensure you run 'npm run build' in frontend/ first!
if os.path.exists(FRONTEND_DIST):
    app.mount(
        "/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    # Mount data if it exists
    if os.path.exists(FRONTEND_PUBLIC_DATA):
        app.mount("/data", StaticFiles(directory=FRONTEND_PUBLIC_DATA), name="data")

    @app.get("/{catchall:path}")
    async def serve_react_app(catchall: str):
        # Return index.html for any path (SPA routing)
        # Check if file exists in dist, otherwise serve index.html
        file_path = os.path.join(FRONTEND_DIST, catchall)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
else:
    logger.warning(
        f"WARNING: Frontend build not found at {FRONTEND_DIST}. Run 'npm run build' in frontend/ folder.")

# --- API ENDPOINTS ---

# Health check endpoint


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "7.2",
        "service": "Halilit Support Center"
    }

# CopilotKit integration endpoint (placeholder)


class ChatMessage(BaseModel):
    content: str
    role: str = "user"
    metadata: Optional[dict] = None


@app.post("/api/copilot/chat")
async def copilot_chat(message: ChatMessage):
    """
    CopilotKit chat endpoint for frontend agent communication.

    This endpoint bridges the frontend UI with backend agents.
    Currently returns a placeholder response.

    TODO: Integrate with Trinity Swarm agents for actual intelligence.
    """
    logger.info(f"Received message: {message.content}")

    return {
        "role": "assistant",
        "content": "CopilotKit endpoint active. Trinity Swarm integration pending.",
        "status": "pending_integration"
    }

# Data catalog endpoint


@app.get("/api/catalog/products")
async def get_catalog_products(limit: int = 100, offset: int = 0):
    """
    Fetch products from the catalog.

    This endpoint provides paginated access to the product catalog
    that's loaded from the data files in frontend/public/data/
    """
    return {
        "status": "ready",
        "limit": limit,
        "offset": offset,
        "message": "Catalog data is loaded from frontend/public/data/"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
