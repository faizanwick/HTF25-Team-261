from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from pymongo import MongoClient, errors

# -------------------------------
# FastAPI App
# -------------------------------
app = FastAPI(title="Voice-Enabled Code Assistant", version="1.0")

# -------------------------------
# MongoDB Atlas Connection
# -------------------------------
MONGO_DETAILS = "mongodb+srv://anaspasha_db:anas%40888@projectdatabase.1lt7ygn.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_DETAILS)
    db = client["project"]             # Database name in MongoDB Atlas
    user_collection = db["database"]   # Collection name inside 'project'
    print("✅ Connected to MongoDB Atlas successfully")
except errors.ConnectionFailure as e:
    print("❌ Could not connect to MongoDB:", e)

# -------------------------------
# Templates
# -------------------------------
templates = Jinja2Templates(directory="Template")

# -------------------------------
# Routes
# -------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return RedirectResponse(url="/signup")

@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup", response_class=HTMLResponse)
def signup_submit(
    request: Request,
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...)
):
    try:
        # Check if email already exists
        if user_collection.find_one({"email": email}):
            return templates.TemplateResponse(
                "signup.html", {"request": request, "error": "Email already registered"}
            )

        # Insert user with plain password (⚠️ not secure)
        user_dict = {
            "username": username,
            "email": email,
            "password": password
        }
        user_collection.insert_one(user_dict)

        return RedirectResponse(url="/login", status_code=303)

    except Exception as e:
        return templates.TemplateResponse(
            "signup.html", {"request": request, "error": f"An error occurred: {e}"}
        )

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

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
                "login.html", {"request": request, "error": "Email not registered"}
            )

        # Compare plain passwords directly (⚠️ not secure)
        if db_user["password"] != password:
            return templates.TemplateResponse(
                "login.html", {"request": request, "error": "Incorrect password"}
            )

        return templates.TemplateResponse(
            "login.html", {"request": request, "message": f"Welcome {db_user['username']}"}
        )

    except Exception as e:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": f"An error occurred: {e}"}
        )

# -------------------------------
# Run command (for reference)
# -------------------------------
# uvicorn main:app --reload
