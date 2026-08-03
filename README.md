# SmartReco AI - Behavioral Recommendation Agent 🚀

An advanced, production-grade behavioral AI recommendation system built for the SmartReco Build Challenge 2026. This platform tracks user actions efficiently and delivers personalized, highly persuasive recommendations driven by an agentic backend.

## 🛠️ Tech Stack
- **Backend:** FastAPI (Python)
- **AI Gateway:** Mesh API (OpenAI SDK compatible)
- **Vector DB:** FAISS (For Semantic Search)
- **Primary DB:** SQLite
- **Frontend:** HTML5, Tailwind CSS, JavaScript (Non-blocking Tracking)

## 🌟 Core Features Implemented
1. **Asynchronous Behavioral Tracking:** Uses optimized JavaScript to capture user clicks and page views without blocking the UI.
2. **Dual-Write Database Engine:** Seamless synchronization between SQLite (relational data) and FAISS Vector DB (semantic data) when courses are updated.
3. **Agentic Recommendation Engine:** A structured reasoning backend that analyzes tracked behavioral events, retrieves contextual products via RAG, and generates tailored persuasive narratives using Mesh API.

## 💻 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd smartreco-agent
   ```

2. **Set up Virtual Environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add:
   ```text
   MESH_API_KEY=your_mesh_api_key
   SUBMISSION_TOKEN=your_submission_token
   ```

5. **Run the Application:**
   ```bash
   uvicorn main:app --reload
   ```
   Open your browser and navigate to `http://localhost:8000`.
