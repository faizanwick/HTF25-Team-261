# CodeWhisper - Voice-Enabled Code Assistant
import speech_recognition as sr
import pyttsx3

def listen_for_command():
    """Listen for voice commands"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    return recognizer.recognize_google(audio)

def process_voice_command(command):
    """Process voice commands and execute them"""
    if "create function" in command.lower():
        return "def new_function():\n    pass"
    elif "add loop" in command.lower():
        return "for i in range(10):\n    print(i)"
    elif "print" in command.lower():
        return 'print("Hello, World!")'
    else:
        return "Command not recognized"

# Example variables
user_name = "Developer"
project_count = 5
is_active = True

# Example loops
for i in range(5):
    print(f"Loop iteration: {i}")

while is_active:
    print("Processing...")
    is_active = False

# Example conditions
if user_name == "Developer":
    print("Welcome back!")
elif project_count > 3:
    print("You have many projects!")
else:
    print("Keep coding!")

# Example class
class VoiceAssistant:
    def __init__(self):
        self.name = "CodeWhisper"
    
    def speak(self, text):
        print(f"{self.name}: {text}")

# Create instance
assistant = VoiceAssistant()
assistant.speak("Ready to help you code!")
def factorial(n):
    """Calculate factorial of n"""
    if n < 0:
        return None
    elif n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

# Example usage
print(f"Factorial of 5: {factorial(5)}")
print(f"Factorial of 0: {factorial(0)}")
def factorial(n):
    """Calculate factorial of n"""
    if n < 0:
        return None
    elif n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

# Example usage
print(f"Factorial of 5: {factorial(5)}")
print(f"Factorial of 0: {factorial(0)}")