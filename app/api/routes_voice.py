from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import requests

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

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@router.post("/process", response_model=VoiceResponse)
async def process_voice(command: VoiceCommand):
    """
    Process voice commands using AI-powered chat API
    """
    try:
        voice_status.last_command = command.command
        voice_status.is_listening = True
        
        # Prepare the prompt for the AI
        system_prompt = f"""You are a helpful coding assistant. When given voice commands, generate appropriate code snippets in {command.language} language.

Rules:
1. Always provide clean, working code
2. Include helpful comments
3. Use proper syntax for the specified language
4. If the command is unclear, ask for clarification
5. Keep responses concise but informative

Common voice commands and their expected outputs:
- "create function" → Generate a function template
- "add loop" → Generate a loop structure
- "print something" → Generate print/output statements
- "if statement" → Generate conditional logic
- "fix errors" → Provide debugging suggestions
- "add comments" → Add explanatory comments

Language: {command.language}
Command: {command.command}"""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "openai/gpt-4-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": f"Voice command: '{command.command}'. Please generate appropriate {command.language} code and provide a brief explanation."
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        # Try AI API first, with fallback to simple responses
        try:
            # Call the OpenRouter API
            response = requests.post(OPENROUTER_URL, headers=headers, json=data)
            response.raise_for_status()
            
            ai_response = response.json()["choices"][0]["message"]["content"]
            
            # Parse the AI response to extract code and explanation
            response_text = ""
            code_generated = ""
            
            # Check if the response contains code blocks
            if "```" in ai_response:
                parts = ai_response.split("```")
                if len(parts) >= 3:
                    # Extract code from code blocks
                    code_generated = parts[1].strip()
                    if code_generated.startswith(command.language):
                        code_generated = code_generated[len(command.language):].strip()
                    response_text = parts[0].strip() + (parts[2].strip() if len(parts) > 2 else "")
                else:
                    response_text = ai_response
            else:
                response_text = ai_response
                
        except Exception as api_error:
            # Fallback to simple rule-based responses if AI fails
            command_lower = command.command.lower()
            
            if "create function" in command_lower or "add function" in command_lower:
                if command.language == "python":
                    code_generated = "def new_function():\n    pass"
                elif command.language == "javascript":
                    code_generated = "function newFunction() {\n    // function body\n}"
                response_text = "Created a new function for you! (Fallback mode)"
                
            elif "add loop" in command_lower or "create loop" in command_lower or "for loop" in command_lower:
                if command.language == "python":
                    code_generated = "for i in range(10):\n    print(i)"
                elif command.language == "javascript":
                    code_generated = "for (let i = 0; i < 10; i++) {\n    console.log(i);\n}"
                response_text = "Added a loop structure! (Fallback mode)"
                
            elif "print" in command_lower or "console" in command_lower:
                if command.language == "python":
                    code_generated = 'print("Hello, World!")'
                elif command.language == "javascript":
                    code_generated = 'console.log("Hello, World!");'
                response_text = "Added a print statement! (Fallback mode)"
                
            else:
                response_text = f"I heard: '{command.command}'. The AI service is temporarily unavailable, but I'm still here to help! (Fallback mode)"
        
        return VoiceResponse(
            received_command=command.command,
            status="success",
            response=response_text,
            code_generated=code_generated
        )
        
    except requests.exceptions.RequestException as e:
        # Fallback to simple response if API fails
        return VoiceResponse(
            received_command=command.command,
            status="success",
            response=f"I received your command: '{command.command}'. The AI service is temporarily unavailable, but I'm working on it!",
            code_generated=""
        )
    except Exception as e:
        # Fallback to simple response for any other errors
        return VoiceResponse(
            received_command=command.command,
            status="success", 
            response=f"I heard: '{command.command}'. There was a technical issue, but I'm here to help!",
            code_generated=""
        )

@router.get("/status", response_model=VoiceStatus)
async def get_voice_status():
    """Get current voice recognition status"""
    return voice_status

@router.post("/toggle")
async def toggle_voice():
    """Toggle voice recognition on/off"""
    voice_status.is_listening = not voice_status.is_listening
    return {"is_listening": voice_status.is_listening, "message": "Voice recognition toggled"}

@router.get("/test-api")
async def test_api():
    """Test if the OpenRouter API is working"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "openai/gpt-4-turbo",
            "messages": [
                {
                    "role": "user", 
                    "content": "Say 'API test successful' if you can read this."
                }
            ],
            "max_tokens": 50,
            "temperature": 0.1
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        response.raise_for_status()
        
        ai_response = response.json()["choices"][0]["message"]["content"]
        
        return {
            "status": "success",
            "message": "API is working",
            "response": ai_response,
            "api_key_status": "valid"
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"API request failed: {str(e)}",
            "api_key_status": "invalid or network error"
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Unexpected error: {str(e)}",
            "api_key_status": "unknown"
        }

@router.get("/commands")
async def get_available_commands():
    """Get list of available voice commands (now AI-powered)"""
    commands = [
        "Create a function",
        "Add a loop", 
        "Add a print statement",
        "Create an if statement",
        "Fix syntax errors",
        "Add comments",
        "Clear the code",
        "Create a class",
        "Add error handling",
        "Generate a data structure",
        "Create a recursive function",
        "Add input validation",
        "Optimize this code",
        "Add unit tests",
        "Create an API endpoint"
    ]
    return {"commands": commands, "note": "Commands are now processed by AI for more intelligent responses"}
