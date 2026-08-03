import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="SmartReco AI Recommendation Agent",
    description="Behavioral AI recommendation engine powered by Mesh API",
    version="1.0.0"
)

# CORS setup to allow frontend to communicate with backend safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI SDK pointing to Mesh API
MESH_API_KEY = os.getenv("MESH_API_KEY")
client = OpenAI(
    base_url="https://meshapi.ai",
    api_key=MESH_API_KEY
)

# Home route to check if server is live
@app.get("/")
def home():
    return {
        "status": "success",
        "message": "SmartReco Agent backend is running successfully!",
        "mesh_api_connected": MESH_API_KEY is not None
    }

# Test route to check Mesh API connectivity
@app.get("/test-ai")
def test_ai():
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": "Say 'Mesh API Connection Successful!'"}]
        )
        return {
            "status": "connected",
            "ai_response": response.choices.message.content
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "failed", "error": str(e)}
        )
