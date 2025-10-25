from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class VoiceCommand(BaseModel):
    command: str

@router.post("/process")
async def process_voice(command: VoiceCommand):
    # Temporary placeholder
    # Later: convert to text -> parse intent -> perform code action
    return {"received_command": command.command, "status": "processing"}
