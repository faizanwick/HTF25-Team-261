from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import requests

router = APIRouter()

class VoiceCommand(BaseModel):
    command: str
    language: Optional[str] = "python"
    action_type: Optional[str] = "code"  # "code", "navigation", "feature", "file"

class VoiceResponse(BaseModel):
    received_command: str
    status: str
    response: Optional[str] = None
    code_generated: Optional[str] = None
    action_type: Optional[str] = None
    action_data: Optional[dict] = None

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
    Process voice commands with hands-free automation support
    """
    try:
        voice_status.last_command = command.command
        voice_status.is_listening = True
        
        command_lower = command.command.lower().strip()
        
        # Determine command type and process accordingly
        action_type, action_data, response_text, code_generated = await process_command_type(
            command_lower, command.language, command.action_type
        )
        
        return VoiceResponse(
            received_command=command.command,
            status="success",
            response=response_text,
            code_generated=code_generated,
            action_type=action_type,
            action_data=action_data
        )
        
    except Exception as e:
        return VoiceResponse(
            received_command=command.command,
            status="success", 
            response=f"I heard: '{command.command}'. There was a technical issue, but I'm here to help!",
            code_generated="",
            action_type="error",
            action_data={"error": str(e)}
        )

async def process_command_type(command_lower: str, language: str, action_type: str):
    """
    Process different types of voice commands
    """
    
    # === VOICE CONTROL COMMANDS ===
    if any(voice in command_lower for voice in ["open voice input", "close voice input", "activate voice", "deactivate voice"]):
        return await handle_voice_control_command(command_lower)
    
    # === NAVIGATION COMMANDS ===
    elif any(nav in command_lower for nav in ["go to", "navigate to", "open", "show", "switch to"]):
        return await handle_navigation_command(command_lower)
    
    # === FEATURE COMMANDS ===
    elif any(feat in command_lower for feat in ["voice search", "analytics", "debug", "shortcuts", "explain"]):
        return await handle_feature_command(command_lower)
    
    # === FILE MANAGEMENT COMMANDS ===
    elif any(file in command_lower for file in ["create file", "new file", "save file", "open file", "delete file"]):
        return await handle_file_command(command_lower, language)
    
    # === CODE GENERATION COMMANDS ===
    else:
        return await handle_code_command(command_lower, language)

async def handle_voice_control_command(command_lower: str):
    """Handle voice input control commands"""
    
    if "open voice input" in command_lower or "activate voice" in command_lower:
        return "voice_control", {"action": "activate_voice_input"}, "Voice input activated! You can now give voice commands.", ""
    
    elif "close voice input" in command_lower or "deactivate voice" in command_lower:
        return "voice_control", {"action": "deactivate_voice_input"}, "Voice input deactivated. Say 'open voice input' to reactivate.", ""
    
    else:
        return "voice_control", {"action": "unknown"}, f"I heard '{command_lower}'. Say 'open voice input' or 'close voice input'.", ""

async def handle_navigation_command(command_lower: str):
    """Handle navigation and UI commands"""
    
    if "home" in command_lower or "landing" in command_lower:
        return "navigation", {"action": "go_to_home"}, "Taking you back to the home page", ""
    
    elif "ide" in command_lower or "editor" in command_lower:
        return "navigation", {"action": "go_to_ide"}, "Opening the IDE interface", ""
    
    elif "menu" in command_lower or "hamburger" in command_lower:
        return "navigation", {"action": "toggle_menu"}, "Opening the feature menu", ""
    
    elif "back" in command_lower:
        return "navigation", {"action": "go_back"}, "Going back to previous view", ""
    
    else:
        return "navigation", {"action": "unknown"}, f"I heard '{command_lower}'. What would you like me to navigate to?", ""

async def handle_feature_command(command_lower: str):
    """Handle feature-specific commands"""
    
    if "voice search" in command_lower:
        return "feature", {"action": "open_voice_search"}, "Opening voice search feature", ""
    
    elif "analytics" in command_lower or "dashboard" in command_lower:
        return "feature", {"action": "open_analytics"}, "Opening analytics dashboard", ""
    
    elif "debug" in command_lower or "auto debug" in command_lower:
        return "feature", {"action": "start_debug"}, "Starting auto debug analysis", ""
    
    elif "shortcuts" in command_lower or "voice shortcuts" in command_lower:
        return "feature", {"action": "open_shortcuts"}, "Opening voice shortcuts manager", ""
    
    elif "explain" in command_lower or "code explanation" in command_lower:
        return "feature", {"action": "explain_code"}, "Analyzing your code for explanation", ""
    
    else:
        return "feature", {"action": "unknown"}, f"I heard '{command_lower}'. Which feature would you like to open?", ""

async def handle_file_command(command_lower: str, language: str):
    """Handle file management commands"""
    
    if "create file" in command_lower or "new file" in command_lower:
        filename = extract_filename_from_command(command_lower)
        return "file", {"action": "create_file", "filename": filename}, f"Creating new file: {filename}", ""
    
    elif "save file" in command_lower:
        return "file", {"action": "save_file"}, "Saving current file", ""
    
    elif "open file" in command_lower:
        filename = extract_filename_from_command(command_lower)
        return "file", {"action": "open_file", "filename": filename}, f"Opening file: {filename}", ""
    
    elif "delete file" in command_lower:
        filename = extract_filename_from_command(command_lower)
        return "file", {"action": "delete_file", "filename": filename}, f"Deleting file: {filename}", ""
    
    else:
        return "file", {"action": "unknown"}, f"I heard '{command_lower}'. What file operation would you like?", ""

async def handle_code_command(command_lower: str, language: str):
    """Handle code generation commands using AI"""
    
    try:
        # Prepare the prompt for the AI
        system_prompt = f"""You are a helpful coding assistant. When given voice commands, generate appropriate code snippets in {language} language.

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
- "for loop" → Generate a for loop
- "while loop" → Generate a while loop
- "class" → Generate a class template
- "import" → Generate import statements

Language: {language}
Command: {command_lower}"""

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
                    "content": f"Voice command: '{command_lower}'. Please generate appropriate {language} code and provide a brief explanation."
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

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
                if code_generated.startswith(language):
                    code_generated = code_generated[len(language):].strip()
                response_text = parts[0].strip() + (parts[2].strip() if len(parts) > 2 else "")
            else:
                response_text = ai_response
        else:
            response_text = ai_response
            
        return "code", {}, response_text, code_generated
        
    except Exception as api_error:
        # Fallback to simple rule-based responses if AI fails
        return await handle_code_fallback(command_lower, language)

async def handle_code_fallback(command_lower: str, language: str):
    """Fallback code generation when AI API fails"""
    
    response_text = ""
    code_generated = ""
    
    if "create function" in command_lower or "add function" in command_lower:
        if language == "python":
            code_generated = "def new_function():\n    pass"
        elif language == "javascript":
            code_generated = "function newFunction() {\n    // function body\n}"
        response_text = "Created a new function for you! (Fallback mode)"
        
    elif "add loop" in command_lower or "create loop" in command_lower or "for loop" in command_lower:
        if language == "python":
            code_generated = "for i in range(10):\n    print(i)"
        elif language == "javascript":
            code_generated = "for (let i = 0; i < 10; i++) {\n    console.log(i);\n}"
        response_text = "Added a loop structure! (Fallback mode)"
        
    elif "while loop" in command_lower:
        if language == "python":
            code_generated = "while True:\n    # Your code here\n    break"
        elif language == "javascript":
            code_generated = "while (true) {\n    // Your code here\n    break;\n}"
        response_text = "Added a while loop! (Fallback mode)"
        
    elif "print" in command_lower or "console" in command_lower:
        if language == "python":
            code_generated = 'print("Hello, World!")'
        elif language == "javascript":
            code_generated = 'console.log("Hello, World!");'
        response_text = "Added a print statement! (Fallback mode)"
        
    elif "if statement" in command_lower or "add condition" in command_lower:
        if language == "python":
            code_generated = "if True:\n    pass"
        elif language == "javascript":
            code_generated = "if (true) {\n    // code here\n}"
        response_text = "Added a conditional statement! (Fallback mode)"
        
    elif "class" in command_lower:
        if language == "python":
            code_generated = "class MyClass:\n    def __init__(self):\n        pass"
        elif language == "javascript":
            code_generated = "class MyClass {\n    constructor() {\n        // constructor code\n    }\n}"
        response_text = "Created a class! (Fallback mode)"
        
    elif "palindrome" in command_lower:
        if language == "python":
            code_generated = '''def is_palindrome(text):
    """Check if a string is a palindrome"""
    text = text.lower().replace(" ", "")
    return text == text[::-1]

# Example usage
word = "racecar"
if is_palindrome(word):
    print(f"{word} is a palindrome!")
else:
    print(f"{word} is not a palindrome.")'''
        elif language == "javascript":
            code_generated = '''function isPalindrome(text) {
    // Remove spaces and convert to lowercase
    const cleanText = text.toLowerCase().replace(/\\s/g, '');
    // Check if text equals its reverse
    return cleanText === cleanText.split('').reverse().join('');
}

// Example usage
const word = "racecar";
if (isPalindrome(word)) {
    console.log(`${word} is a palindrome!`);
} else {
    console.log(`${word} is not a palindrome.`);
}'''
        response_text = "Created a palindrome checker function! (Fallback mode)"
        
    elif "fibonacci" in command_lower:
        if language == "python":
            code_generated = '''def fibonacci(n):
    """Generate Fibonacci sequence up to n terms"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

# Example usage
print(fibonacci(10))'''
        elif language == "javascript":
            code_generated = '''function fibonacci(n) {
    if (n <= 0) return [];
    if (n === 1) return [0];
    if (n === 2) return [0, 1];
    
    const fib = [0, 1];
    for (let i = 2; i < n; i++) {
        fib.push(fib[i-1] + fib[i-2]);
    }
    return fib;
}

// Example usage
console.log(fibonacci(10));'''
        response_text = "Created a Fibonacci sequence generator! (Fallback mode)"
        
    elif "sort" in command_lower or "bubble sort" in command_lower:
        if language == "python":
            code_generated = '''def bubble_sort(arr):
    """Sort array using bubble sort algorithm"""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# Example usage
numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = bubble_sort(numbers.copy())
print(f"Original: {numbers}")
print(f"Sorted: {sorted_numbers}")'''
        elif language == "javascript":
            code_generated = '''function bubbleSort(arr) {
    const n = arr.length;
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
            }
        }
    }
    return arr;
}

// Example usage
const numbers = [64, 34, 25, 12, 22, 11, 90];
const sortedNumbers = bubbleSort([...numbers]);
console.log(`Original: ${numbers}`);
console.log(`Sorted: ${sortedNumbers}`);'''
        response_text = "Created a bubble sort algorithm! (Fallback mode)"
        
    elif "binary search" in command_lower:
        if language == "python":
            code_generated = '''def binary_search(arr, target):
    """Binary search algorithm"""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Not found

# Example usage
sorted_array = [1, 3, 5, 7, 9, 11, 13, 15]
target = 7
result = binary_search(sorted_array, target)
if result != -1:
    print(f"Found {target} at index {result}")
else:
    print(f"{target} not found")'''
        elif language == "javascript":
            code_generated = '''function binarySearch(arr, target) {
    let left = 0;
    let right = arr.length - 1;
    
    while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        if (arr[mid] === target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    
    return -1; // Not found
}

// Example usage
const sortedArray = [1, 3, 5, 7, 9, 11, 13, 15];
const target = 7;
const result = binarySearch(sortedArray, target);
if (result !== -1) {
    console.log(`Found ${target} at index ${result}`);
} else {
    console.log(`${target} not found`);
}'''
        response_text = "Created a binary search algorithm! (Fallback mode)"
        
    elif "prime" in command_lower:
        if language == "python":
            code_generated = '''def is_prime(n):
    """Check if a number is prime"""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate_primes(limit):
    """Generate all prime numbers up to limit"""
    primes = []
    for i in range(2, limit + 1):
        if is_prime(i):
            primes.append(i)
    return primes

# Example usage
print(f"Is 17 prime? {is_prime(17)}")
print(f"Primes up to 20: {generate_primes(20)}")'''
        elif language == "javascript":
            code_generated = '''function isPrime(n) {
    if (n < 2) return false;
    for (let i = 2; i <= Math.sqrt(n); i++) {
        if (n % i === 0) return false;
    }
    return true;
}

function generatePrimes(limit) {
    const primes = [];
    for (let i = 2; i <= limit; i++) {
        if (isPrime(i)) {
            primes.push(i);
        }
    }
    return primes;
}

// Example usage
console.log(`Is 17 prime? ${isPrime(17)}`);
console.log(`Primes up to 20: ${generatePrimes(20)}`);'''
        response_text = "Created prime number functions! (Fallback mode)"
        
    elif "factorial" in command_lower:
        if language == "python":
            code_generated = '''def factorial(n):
    """Calculate factorial of n"""
    if n < 0:
        return None
    elif n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

# Example usage
print(f"Factorial of 5: {factorial(5)}")
print(f"Factorial of 0: {factorial(0)}")'''
        elif language == "javascript":
            code_generated = '''function factorial(n) {
    if (n < 0) return null;
    if (n === 0 || n === 1) return 1;
    return n * factorial(n - 1);
}

// Example usage
console.log(`Factorial of 5: ${factorial(5)}`);
console.log(`Factorial of 0: ${factorial(0)}`);'''
        response_text = "Created a factorial function! (Fallback mode)"
        
    else:
        response_text = f"I heard: '{command_lower}'. The AI service is temporarily unavailable, but I'm still here to help! (Fallback mode)"
    
    return "code", {}, response_text, code_generated

def extract_filename_from_command(command: str):
    """Extract filename from voice command"""
    # Simple filename extraction - can be enhanced
    words = command.split()
    for i, word in enumerate(words):
        if word in ["file", "create", "new", "open", "delete"] and i + 1 < len(words):
            return words[i + 1]
    return "new_file.py"

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
    """Get comprehensive list of hands-free voice commands"""
    
    commands = {
        "voice_control": {
            "description": "Control voice input activation",
            "commands": [
                "Open voice input",
                "Close voice input", 
                "Activate voice",
                "Deactivate voice"
            ]
        },
        "navigation": {
            "description": "Navigate the interface hands-free",
            "commands": [
                "Go to home",
                "Go to IDE", 
                "Open menu",
                "Go back",
                "Switch to editor"
            ]
        },
        "features": {
            "description": "Open and control features",
            "commands": [
                "Open voice search",
                "Open analytics dashboard", 
                "Start auto debug",
                "Open voice shortcuts",
                "Explain code"
            ]
        },
        "file_management": {
            "description": "Manage files hands-free",
            "commands": [
                "Create new file",
                "Save file",
                "Open file [filename]",
                "Delete file [filename]"
            ]
        },
        "code_generation": {
            "description": "Generate code with AI",
            "commands": [
                "Create function",
                "Add for loop",
                "Add while loop", 
                "Add if statement",
                "Add print statement",
                "Create class",
                "Add comments",
        "Fix syntax errors",
                "Palindrome checker",
                "Fibonacci sequence",
                "Bubble sort",
                "Binary search",
                "Prime numbers",
                "Factorial function"
            ]
        },
        "advanced": {
            "description": "Advanced coding commands",
            "commands": [
                "Generate API endpoint",
                "Add error handling",
                "Create data structure",
                "Add unit tests",
                "Optimize code",
                "Add input validation"
            ]
        }
    }
    
    return {
        "commands": commands,
        "note": "All commands are processed by AI for intelligent responses. Say any command naturally!",
        "examples": [
            "Say 'open voice input' to activate voice commands",
            "Say 'close voice input' to deactivate voice commands",
            "Say 'open voice search' to open the search feature",
            "Say 'create new file main.py' to create a file",
            "Say 'go to home' to navigate back",
            "Say 'for loop' to generate loop code"
        ]
    }
