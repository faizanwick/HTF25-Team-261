from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json

router = APIRouter()

class VoiceCommand(BaseModel):
    command: str
    language: Optional[str] = "python"

class VoiceResponse(BaseModel):
    received_command: str
    status: str
    response: Optional[str] = None
    code_generated: Optional[str] = None

class VoiceStatus(BaseModel):
    is_listening: bool
    last_command: Optional[str] = None

# In-memory storage for demo purposes
voice_status = VoiceStatus(is_listening=False, last_command=None)

@router.post("/process", response_model=VoiceResponse)
async def process_voice(command: VoiceCommand):
    """
    Process voice commands and return appropriate responses
    """
    try:
        voice_status.last_command = command.command
        voice_status.is_listening = True
        
        # Simple command processing logic
        response_text = ""
        code_generated = ""
        
        command_lower = command.command.lower()
        
        if "create function" in command_lower or "add function" in command_lower:
            if command.language == "python":
                code_generated = "def new_function():\n    pass"
            elif command.language == "javascript":
                code_generated = "function newFunction() {\n    // function body\n}"
            response_text = "Created a new function for you!"
            
        elif "add loop" in command_lower or "create loop" in command_lower:
            if command.language == "python":
                code_generated = "for i in range(10):\n    print(i)"
            elif command.language == "javascript":
                code_generated = "for (let i = 0; i < 10; i++) {\n    console.log(i);\n}"
            response_text = "Added a loop structure!"
            
        elif "print" in command_lower or "console" in command_lower:
            if command.language == "python":
                code_generated = 'print("Hello, World!")'
            elif command.language == "javascript":
                code_generated = 'console.log("Hello, World!");'
            response_text = "Added a print statement!"
            
        elif "if statement" in command_lower or "add condition" in command_lower:
            if command.language == "python":
                code_generated = "if True:\n    pass"
            elif command.language == "javascript":
                code_generated = "if (true) {\n    // code here\n}"
            response_text = "Added a conditional statement!"
            
        elif "fix" in command_lower or "debug" in command_lower:
            response_text = "Analyzing code for issues... No syntax errors found!"
            
        elif "comment" in command_lower:
            if command.language == "python":
                code_generated = "# Add your comment here"
            elif command.language == "javascript":
                code_generated = "// Add your comment here"
            response_text = "Added a comment!"
            
        else:
            response_text = f"Command '{command.command}' received. I'm processing it..."
        
        return VoiceResponse(
            received_command=command.command,
            status="success",
            response=response_text,
            code_generated=code_generated
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing voice command: {str(e)}")

@router.get("/status", response_model=VoiceStatus)
async def get_voice_status():
    """Get current voice recognition status"""
    return voice_status

@router.post("/toggle")
async def toggle_voice():
    """Toggle voice recognition on/off"""
    voice_status.is_listening = not voice_status.is_listening
    return {"is_listening": voice_status.is_listening, "message": "Voice recognition toggled"}

@router.get("/commands")
async def get_available_commands():
    """Get list of available voice commands"""
    commands = [
        "Create a function",
        "Add a loop", 
        "Add a print statement",
        "Create an if statement",
        "Fix syntax errors",
        "Add comments",
        "Clear the code"
    ]
    return {"commands": commands}
