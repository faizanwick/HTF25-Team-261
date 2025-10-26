from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from app.api import routes_voice, routes_code

app = FastAPI(title="Voice-Enabled Code Assistant", version="1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(routes_voice.router, prefix="/voice", tags=["Voice Commands"])
app.include_router(routes_code.router, prefix="/code", tags=["Code Operations"])

# Serve static files
template_dir = os.path.join(os.path.dirname(__file__), "..", "template")
app.mount("/static", StaticFiles(directory=template_dir), name="static")

@app.get("/")
def root():
    # Serve the main HTML file
    template_path = os.path.join(template_dir, "index.html")
    if os.path.exists(template_path):
        return FileResponse(template_path)
    return {"message": "Voice-Enabled Code Assistant API is running 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Voice-Enabled Code Assistant is running 🚀"}
