from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import time
import os
from datetime import datetime

from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.api.v1.router import api_router  # Import your existing router

# Import models for table creation
from app.models.user import User
from app.models.detection import Detection, DetectedObject
from app.models.product import ProductPosition

# Wait for database to be ready
def wait_for_db():
    max_retries = 10
    retry_delay = 5
    
    for i in range(max_retries):
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            print("✅ Database connection successful!")
            return True
        except Exception as e:
            print(f"❌ Database connection failed (attempt {i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                print(f"🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    print("❌ Could not connect to database after all retries")
    return False

# Create database tables
if wait_for_db():
    Base.metadata.create_all(bind=engine)
else:
    print("⚠️ Skipping database table creation due to connection failure")

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Retail Product Detection and Analysis API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://frontend:3000", 
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://retail_vision_frontend:3000",
        "http://0.0.0.0:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include your existing API router
app.include_router(api_router, prefix="/api/v1")

# Health checks and root endpoints
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    
    # Create upload directories
    upload_dirs = [
        os.path.join(settings.UPLOAD_DIR, "original"),
        os.path.join(settings.UPLOAD_DIR, "annotated"), 
        os.path.join(settings.UPLOAD_DIR, "thumbnails")
    ]
    
    for dir_path in upload_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")
    
    print("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    print(f"👋 {settings.APP_NAME} shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.DEBUG else False
    )