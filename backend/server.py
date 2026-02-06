from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

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
    print(
        f"WARNING: Frontend build not found at {FRONTEND_DIST}. Run 'npm run build' in frontend/ folder.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
