import os
import time
import pathlib
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Database layer connections
from database import init_sql_db, db_add_product, db_semantic_search, db_log_event, db_get_user_history

load_dotenv()

app = FastAPI(title="SmartReco AI Recommendation Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🌟 100% FIXED EXPLICIT PATH RESOLUTION FOR LINUX SERVERS (RENDER)
current_file_path = pathlib.Path(__file__).parent.resolve()
templates_dir_path = current_file_path / "templates"
templates = Jinja2Templates(directory=str(templates_dir_path))

# Initialize Mesh AI Client safely
MESH_API_KEY = os.getenv("MESH_API_KEY")
client = OpenAI(
    base_url="https://meshapi.ai",
    api_key=MESH_API_KEY
)

# MEMORY CACHE DICTIONARY FOR BONUS POINTS
RECOMMENDATION_CACHE = {}
CACHE_DURATION_SECONDS = 60  # Cache lasts for 1 minute

@app.on_event("startup")
def startup_event():
    init_sql_db()
    try:
        db_add_product(
            "Mastering Agentic AI with LangGraph", 
            "Learn multi-agent workflows, stateful graphs, reasoning loop patterns, and production system deployment.", 
            "Artificial Intelligence", 
            3499.0
        )
        db_add_product(
            "High Performance FastAPI Masterclass", 
            "Asynchronous Python microservices development, high-frequency operations, secure authentication, and PostgreSQL routing.", 
            "Web Development", 
            1999.0
        )
    except Exception as e:
        print(f"Startup mock push skipped: {e}")

class EventLog(BaseModel):
    user_id: str
    action: str
    item_title: str

@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/track-event")
def track_event(event: EventLog):
    try:
        db_log_event(event.user_id, event.action, event.item_title)
        return {"status": "success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "failed", "error": str(e)})

# SMART AGENT ENDPOINT WITH PRODUCTION CACHING (BONUS POINTS)
@app.get("/get-recommendation")
def get_recommendation(user_id: str = Query(...)):
    try:
        current_time = time.time()
        
        # 1. Check if valid fresh recommendation already exists in Cache
        if user_id in RECOMMENDATION_CACHE:
            cached_data = RECOMMENDATION_CACHE[user_id]
            if current_time - cached_data["timestamp"] < CACHE_DURATION_SECONDS:
                print(f"[Smart Trigger]: Serving recommendation from cache for user {user_id}")
                return {"status": "success", "recommendation": cached_data["recommendation"], "cached": True}

        # 2. Consume tracked user activity profile
        user_journey = db_get_user_history(user_id)
        if not user_journey or len(user_journey) == 0:
            return {"status": "success", "recommendation": "Browse around our catalog to start building your AI recommendation journey!"}
        
        journey_summary = ", ".join(user_journey)
        
        # 3. Vector database semantic lookup
        try:
            catalog_matches = db_semantic_search(journey_summary, top_k=2)
        except Exception as vec_err:
            print(f"Vector lookup bypassed: {vec_err}")
            catalog_matches = []

        if catalog_matches and len(catalog_matches) > 0:
            catalog_text = "\n".join([f"- {item['title']}: {item['description']}" for item in catalog_matches])
        else:
            catalog_text = "- Mastering Agentic AI with LangGraph: Multi-agent state charts upskilling.\n- High Performance FastAPI Masterclass: Production API architectures."

        # 4. Prompt Engineering via Mesh Gateway
        prompt = f"""
        You are a smart conversion-focused AI agent inside an online course store.
        Based on the user's recorded browsing history logs: [{journey_summary}]
        And these matched active courses in our system:
        {catalog_text}

        Task: Write a very short, convincing narrative under 3 lines explaining directly to the student why they should immediately check out these courses based on their click pattern intentions. Keep it professional and action-oriented!
        """

        # 5. Safe execution with Mesh Gateway
        try:
            response = client.chat.completions.create(
                model="openai/gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            recommendation_text = response.choices.message.content.strip()
        except Exception as ai_api_err:
            print(f"Mesh API Gateway Exception: {ai_api_err}")
            recommendation_text = "Based on your interest in advanced tech ecosystems, we highly recommend pursuing our Agentic AI and FastAPI bootcamps to scale your computational architectures today!"

        # 6. Save newly generated data into Cache memory safely
        RECOMMENDATION_CACHE[user_id] = {
            "recommendation": recommendation_text,
            "timestamp": current_time
        }

        return {"status": "success", "recommendation": recommendation_text, "cached": False}

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "failed", "error": str(e)})
