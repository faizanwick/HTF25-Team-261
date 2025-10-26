from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from pymongo import MongoClient, errors
import requests
import os
from app.api import routes_voice, routes_code

# -------------------------------
# FastAPI App
# -------------------------------
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

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Voice-Enabled Code Assistant is running 🚀"}
# -------------------------------
# MongoDB Atlas Connection
# -------------------------------
MONGO_DETAILS = "mongodb+srv://anaspasha_db:anas%40888@projectdatabase.1lt7ygn.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_DETAILS)
    db = client["project"]
    user_collection = db["database"]
    print("✅ Connected to MongoDB Atlas successfully")
except errors.ConnectionFailure as e:
    print("❌ Could not connect to MongoDB:", e)

# -------------------------------
# Templates
# -------------------------------
templates = Jinja2Templates(directory="template")

# -------------------------------
# OpenRouter Configuration
# -------------------------------
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# -------------------------------
# Chat limits
# -------------------------------
MAX_MESSAGE_LENGTH = 500  # limit user input

# -------------------------------
# Routes
# -------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return RedirectResponse(url="/signup")

@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request, "action": "signup"})

@app.post("/signup", response_class=HTMLResponse)
def signup_submit(
    request: Request,
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...)
):
    try:
        if user_collection.find_one({"email": email}):
            return templates.TemplateResponse(
                "auth.html", {"request": request, "error": "Email already registered", "action": "signup"}
            )
        user_dict = {"username": username, "email": email, "password": password}
        user_collection.insert_one(user_dict)
        return RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "auth.html", {"request": request, "error": f"An error occurred: {e}", "action": "signup"}
        )

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request, "action": "login"})

@app.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    email: EmailStr = Form(...),
    password: str = Form(...)
):
    try:
        db_user = user_collection.find_one({"email": email})
        if not db_user:
            return templates.TemplateResponse(
                "auth.html", {"request": request, "error": "Email not registered", "action": "login"}
            )
        if db_user["password"] != password:
            return templates.TemplateResponse(
                "auth.html", {"request": request, "error": "Incorrect password", "action": "login"}
            )
        return RedirectResponse(url="/chat", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "auth.html", {"request": request, "error": f"An error occurred: {e}", "action": "login"}
        )

# -------------------------------
# Chat Page
# -------------------------------
@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# -------------------------------
# Chat API Endpoint (OpenRouter)
# -------------------------------
@app.post("/chat", response_class=HTMLResponse)
def chat_response(request: Request, user_message: str = Form(...)):
    user_message = user_message[:MAX_MESSAGE_LENGTH]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "openai/gpt-4-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful coding assistant. "
                           "Answer clearly in 5-10 lines maximum."
            },
            {"role": "user", "content": user_message + " give me consise answer."}
        ],
        "max_tokens": 200,      # limit response length
        "temperature": 0.5      # keep answers concise
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        return templates.TemplateResponse(
            "chat.html",
            {"request": request, "user_message": user_message, "reply": reply}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "chat.html",
            {"request": request, "error": f"Chat error: {e}"}
        )

# -------------------------------
# Run command:
# uvicorn main:app --reload
# -------------------------------
