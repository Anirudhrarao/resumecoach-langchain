import sys 
import os 

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import router


app = FastAPI(
    title="ResumeCoach API",
    description="AI-powered resume analyzer and career coach",
    version="1.0.0"
)

# Allow the frontend (any origin in dev) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routes from routes.py under /api prefix
app.include_router(router, prefix="/api")

# Serve the frontend HTML as the root page
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "frontend")),
    name="static"
)

@app.get("/")
def serve_frontend():
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    )


PORT = int(os.getenv("PORT", 8000))