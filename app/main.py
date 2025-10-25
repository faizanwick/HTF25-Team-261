from fastapi import FastAPI
from app.api import routes_voice, routes_code

app = FastAPI(title="Voice-Enabled Code Assistant", version="1.0")

# Include Routers
app.include_router(routes_voice.router, prefix="/voice", tags=["Voice Commands"])
app.include_router(routes_code.router, prefix="/code", tags=["Code Operations"])

@app.get("/")
def root():
    return {"message": "Voice-Enabled Code Assistant API is running 🚀"}
