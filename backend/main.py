"""
Skin Disease Detection - FastAPI Application
=============================================
Main entry point for the AI-Based Skin Disease Detection API.

Features:
    - JWT-based authentication (signup/login)
    - Image upload and CNN-based prediction
    - Prediction history
    - Admin panel APIs
    - Static file serving for frontend

Run:
    uvicorn backend.main:app --reload --port 8000
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from backend.config import settings
from backend.routes import auth, prediction, admin
from backend.utils.ml_predictor import predictor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Loads the ML model on startup and cleans up on shutdown.
    """
    # ── Startup ──
    print("=" * 50)
    print("  SKIN DISEASE DETECTION API")
    print("=" * 50)
    
    # Load ML model
    predictor.load_model(settings.MODEL_PATH)
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    if predictor.is_loaded:
        print("[✓] ML Model loaded successfully")
    else:
        print("[✗] ML Model not found — run 'python ml_model/create_demo_model.py'")
    
    print(f"[✓] MongoDB URI: {settings.MONGODB_URI}")
    print(f"[✓] Upload directory: {settings.UPLOAD_DIR}")
    print("=" * 50)
    
    yield
    
    # ── Shutdown ──
    print("\n[INFO] Shutting down application...")


# ──────────────────────────────────────────────
# Create FastAPI Application
# ──────────────────────────────────────────────

app = FastAPI(
    title="AI-Based Skin Disease Detection",
    description="Web application for automated skin disease classification using CNN",
    version="1.0.0",
    lifespan=lifespan
)

# ──────────────────────────────────────────────
# CORS Middleware
# ──────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Register API Routes
# ──────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(prediction.router)
app.include_router(admin.router)

# ──────────────────────────────────────────────
# Static File Serving
# ──────────────────────────────────────────────

# Serve uploaded images
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Serve frontend static files (CSS, JS)
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")


# ──────────────────────────────────────────────
# Frontend Page Routes
# ──────────────────────────────────────────────

def serve_page(page_name: str):
    """Helper to serve frontend HTML pages."""
    file_path = os.path.join(frontend_dir, page_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    return HTMLResponse("<h1>Page not found</h1>", status_code=404)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the login page as the default landing page."""
    return serve_page("index.html")


@app.get("/signup", response_class=HTMLResponse)
async def signup_page():
    """Serve the signup page."""
    return serve_page("signup.html")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Serve the dashboard page."""
    return serve_page("dashboard.html")


@app.get("/predict", response_class=HTMLResponse)
async def predict_page():
    """Serve the prediction/upload page."""
    return serve_page("predict.html")


@app.get("/history", response_class=HTMLResponse)
async def history_page():
    """Serve the history page."""
    return serve_page("history.html")


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """Serve the admin panel page."""
    return serve_page("admin.html")


@app.get("/report", response_class=HTMLResponse)
async def report_page():
    """Serve the academic report."""
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
    file_path = os.path.join(docs_dir, "report.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    return HTMLResponse("<h1>Report not found</h1>", status_code=404)


@app.get("/presentation", response_class=HTMLResponse)
async def presentation_page():
    """Serve the HTML presentation."""
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
    file_path = os.path.join(docs_dir, "presentation.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    return HTMLResponse("<h1>Presentation not found</h1>", status_code=404)


# Serve sample images
sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_images")
if os.path.isdir(sample_dir):
    app.mount("/sample_images", StaticFiles(directory=sample_dir), name="sample_images")


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": predictor.is_loaded,
        "version": "1.0.0"
    }


# ──────────────────────────────────────────────
# Run with: uvicorn backend.main:app --reload --port 8000
# ──────────────────────────────────────────────
