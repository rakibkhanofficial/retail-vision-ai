from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
import time
from typing import List, Optional
import os
import uuid
import json
import aiofiles
from pathlib import Path
from datetime import datetime
from PIL import Image

# Import configurations and utilities
from app.core.config import settings
from app.db.session import get_db, SessionLocal, engine
from app.db.base import Base

# Import models
from app.models.user import User
from app.models.detection import Detection, DetectedObject
from app.models.product import ProductPosition

# Import schemas
from app.schemas.user import UserCreate, UserResponse, Token
from app.schemas.detection import DetectionResponse, QuestionRequest, QuestionResponse

# Import services
from app.services.yolo_service import YOLODetectionService
from app.services.gemini_service import GeminiAnalysisService

# Import security utilities
from app.core.security import SecurityUtils

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

    # Initialize services with error handling
try:
    yolo_service = YOLODetectionService()
    print("✅ YOLO service initialized successfully")
except Exception as e:
    print(f"❌ YOLO service initialization failed: {e}")
    print("⚠️  Object detection will not be available")
    yolo_service = None

gemini_service = GeminiAnalysisService() if settings.GEMINI_API_KEY else None
if gemini_service and gemini_service.model:
    print("✅ Gemini service initialized successfully")
else:
    print("⚠️  Gemini service not available (GEMINI_API_KEY not configured)")

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize services
yolo_service = YOLODetectionService()
gemini_service = GeminiAnalysisService() if settings.GEMINI_API_KEY else None

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Retail Product Detection and Analysis API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://frontend:3000", "http://localhost:3001"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://frontend:3000", 
        "http://localhost:3001",  # Make sure this is included
        "http://127.0.0.1:3001",   # Add this as well
        "http://retail_vision_frontend:3000",
        "http://0.0.0.0:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ============================================================================
# DEPENDENCY FUNCTIONS
# ============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = SecurityUtils.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=SecurityUtils.get_password_hash(user_data.password)
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# Login request model
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/v1/auth/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user and return access token - JSON only"""
    # Find user
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not SecurityUtils.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Create access token
    access_token = SecurityUtils.create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user
# ============================================================================
# DETECTION ENDPOINTS
# ============================================================================

@app.post("/api/v1/detections", response_model=DetectionResponse, status_code=status.HTTP_201_CREATED)
async def create_detection(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload image and perform object detection"""
    # Validate file
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())
    original_filename = f"{unique_id}{file_ext}"
    annotated_filename = f"{unique_id}_annotated{file_ext}"
    thumbnail_filename = f"{unique_id}_thumb.jpg"
    
    original_path = os.path.join(settings.UPLOAD_DIR, "original", original_filename)
    annotated_path = os.path.join(settings.UPLOAD_DIR, "annotated", annotated_filename)
    thumbnail_path = os.path.join(settings.UPLOAD_DIR, "thumbnails", thumbnail_filename)
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(original_path), exist_ok=True)
    os.makedirs(os.path.dirname(annotated_path), exist_ok=True)
    os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
    
    # Save uploaded file
    try:
        async with aiofiles.open(original_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Run YOLO detection
    try:
        detections, analysis = yolo_service.detect_objects(original_path, annotated_path)
        
        # Create thumbnail
        yolo_service.create_thumbnail(annotated_path, thumbnail_path)
        
        # Get image dimensions
        img = Image.open(original_path)
        img_width, img_height = img.size
        
    except Exception as e:
        # Cleanup files
        for path in [original_path, annotated_path, thumbnail_path]:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
    
    # Perform Gemini analysis for retail products - with proper error handling
    retail_analysis = {
        "brands_detected": [],
        "product_categories": [],
        "positioning_analysis": "Gemini analysis not available due to API quota limits",
        "recommendations": [],
        "positioning_details": []
    }
    
    if gemini_service:
        try:
            retail_analysis = gemini_service.analyze_retail_products(
                annotated_path, detections, analysis
            )
            # Ensure retail_analysis is always a dictionary
            if not isinstance(retail_analysis, dict):
                retail_analysis = {
                    "brands_detected": [],
                    "product_categories": [],
                    "positioning_analysis": "Analysis completed but returned unexpected format",
                    "recommendations": [],
                    "positioning_details": []
                }
                
        except Exception as e:
            print(f"Retail analysis error: {e}")
            # Create a proper error structure instead of error string
            retail_analysis = {
                "brands_detected": [],
                "product_categories": [],
                "positioning_analysis": f"Gemini analysis unavailable: {str(e)}",
                "recommendations": ["Please check your Gemini API quota and billing settings"],
                "positioning_details": []
            }
    
    # Merge with YOLO analysis - ensure analysis is always a proper dictionary
    if not isinstance(analysis, dict):
        analysis = {}
    
    analysis["retail_analysis"] = retail_analysis
    
    # Ensure analysis_data is JSON serializable and valid
    try:
        # Validate that analysis is a proper dictionary
        analysis_data_str = json.dumps(analysis)
        # Test that it can be loaded back (this will catch any serialization issues)
        analysis_data_valid = json.loads(analysis_data_str)
    except (TypeError, ValueError) as e:
        print(f"Analysis data serialization error: {e}")
        # Create a safe fallback analysis data
        analysis = {
            "total_objects": len(detections),
            "class_distribution": {},
            "avg_confidence": 0.0,
            "image_dimensions": {"width": img_width, "height": img_height},
            "retail_analysis": retail_analysis
        }
    
    # Save to database
    db_detection = Detection(
        user_id=current_user.id,
        name=name or f"Detection {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        original_image=f"/uploads/original/{original_filename}",
        annotated_image=f"/uploads/annotated/{annotated_filename}",
        thumbnail=f"/uploads/thumbnails/{thumbnail_filename}",
        image_width=img_width,
        image_height=img_height,
        total_objects=len(detections),
        analysis_data=json.dumps(analysis)
    )
    
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    
    # Save detected objects
    for det in detections:
        db_object = DetectedObject(
            detection_id=db_detection.id,
            class_name=det["class_name"],
            confidence=det["confidence"],
            x_min=det["x_min"],
            y_min=det["y_min"],
            x_max=det["x_max"],
            y_max=det["y_max"],
            center_x=det.get("center_x"),
            center_y=det.get("center_y"),
            width=det.get("width"),
            height=det.get("height"),
            area=det.get("area")
        )
        db.add(db_object)
    
    # Save product positions (if available from retail analysis)
    if retail_analysis.get("positioning_details"):
        for product_info in retail_analysis.get("positioning_details", []):
            if isinstance(product_info, dict):
                db_product = ProductPosition(
                    detection_id=db_detection.id,
                    product_name=product_info.get("name", "Unknown"),
                    brand=product_info.get("brand"),
                    shelf_row=product_info.get("row"),
                    shelf_column=product_info.get("column"),
                    position_description=product_info.get("description"),
                    quantity=product_info.get("quantity", 1),
                    confidence=product_info.get("confidence", 0.5),
                    x_min=product_info.get("x_min", 0),
                    y_min=product_info.get("y_min", 0),
                    x_max=product_info.get("x_max", 0),
                    y_max=product_info.get("y_max", 0)
                )
                db.add(db_product)
    
    db.commit()
    db.refresh(db_detection)
    
    return db_detection

@app.get("/api/v1/detections", response_model=List[DetectionResponse])
async def list_detections(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of user's detections"""
    detections = db.query(Detection)\
        .filter(Detection.user_id == current_user.id)\
        .order_by(Detection.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return detections

@app.get("/api/v1/detections/{detection_id}", response_model=DetectionResponse)
async def get_detection(
    detection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific detection by ID"""
    detection = db.query(Detection).filter(
        Detection.id == detection_id,
        Detection.user_id == current_user.id
    ).first()
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    return detection

@app.delete("/api/v1/detections/{detection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_detection(
    detection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a detection"""
    detection = db.query(Detection).filter(
        Detection.id == detection_id,
        Detection.user_id == current_user.id
    ).first()
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    # Delete associated files
    for image_path in [detection.original_image, detection.annotated_image, detection.thumbnail]:
        if image_path:
            full_path = os.path.join("/app", image_path.lstrip("/"))
            if os.path.exists(full_path):
                os.remove(full_path)
    
    # Delete from database (cascades to objects and products)
    db.delete(detection)
    db.commit()
    
    return None

# ============================================================================
# ANALYSIS & Q&A ENDPOINTS
# ============================================================================

@app.post("/api/v1/analysis/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about a detection"""
    # Get detection
    detection = db.query(Detection).filter(
        Detection.id == request.detection_id,
        Detection.user_id == current_user.id
    ).first()
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    # Get detected objects
    objects = [
        {
            "class_name": obj.class_name,
            "confidence": obj.confidence,
            "x_min": obj.x_min,
            "y_min": obj.y_min,
            "x_max": obj.x_max,
            "y_max": obj.y_max,
            "center_x": obj.center_x,
            "center_y": obj.center_y
        }
        for obj in detection.objects
    ]
    
    # Check if Gemini service is available
    if not gemini_service or not gemini_service.model:
        # Provide a helpful fallback response
        fallback_answer = self._generate_fallback_answer(request.question, detection, objects)
        return {
            "answer": fallback_answer,
            "detection_id": detection.id
        }
    
    # Get answer from Gemini
    try:
        print(f"🔍 Asking question about detection {detection.id}: {request.question}")
        answer = gemini_service.answer_question(request.question, detection, objects)
        print("✅ Question answered successfully")
        
    except Exception as e:
        print(f"❌ Gemini Q&A error: {e}")
        # Provide fallback instead of failing completely
        fallback_answer = self._generate_fallback_answer(request.question, detection, objects, str(e))
        answer = fallback_answer
    
    return {
        "answer": answer,
        "detection_id": detection.id
    }

def _generate_fallback_answer(self, question: str, detection: Detection, objects: List[Dict], error_msg: str = "") -> str:
    """Generate a fallback answer when Gemini is unavailable"""
    question_lower = question.lower()
    
    # Basic question answering based on detection data
    if any(word in question_lower for word in ['how many', 'count', 'number']):
        object_count = len(objects)
        class_summary = {}
        for obj in objects:
            class_summary[obj['class_name']] = class_summary.get(obj['class_name'], 0) + 1
        
        class_details = ", ".join([f"{count} {cls}" for cls, count in class_summary.items()])
        return f"I detected {object_count} objects in total: {class_details}. " + \
               (f"(Note: AI analysis is currently unavailable due to: {error_msg})" if error_msg else "")
    
    elif any(word in question_lower for word in ['what', 'detect', 'see', 'find']):
        classes = list(set(obj['class_name'] for obj in objects))
        class_list = ", ".join(classes)
        return f"I detected the following objects: {class_list}. " + \
               (f"(AI analysis limited due to: {error_msg})" if error_msg else "")
    
    elif any(word in question_lower for word in ['where', 'position', 'location']):
        return "I can detect object positions, but detailed spatial analysis requires the AI service which is currently unavailable. " + \
               (f"Error: {error_msg}" if error_msg else "")
    
    else:
        return "I can answer basic questions about detected objects, but detailed analysis is currently unavailable. " + \
               (f"AI service error: {error_msg}" if error_msg else "Please check your Gemini API configuration.")

@app.get("/api/v1/analysis/statistics")
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's detection statistics"""
    try:
        total_detections = db.query(Detection).filter(Detection.user_id == current_user.id).count()
        total_objects = db.query(DetectedObject).join(Detection).filter(Detection.user_id == current_user.id).count()
        
        # Get class distribution across all detections
        objects = db.query(DetectedObject).join(Detection).filter(Detection.user_id == current_user.id).all()
        class_counts = {}
        for obj in objects:
            class_counts[obj.class_name] = class_counts.get(obj.class_name, 0) + 1
        
        # Calculate detection frequency (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_detections = db.query(Detection).filter(
            Detection.user_id == current_user.id,
            Detection.created_at >= thirty_days_ago
        ).count()
        
        # Most active day
        daily_counts = db.query(
            func.date(Detection.created_at).label('date'),
            func.count(Detection.id).label('count')
        ).filter(
            Detection.user_id == current_user.id
        ).group_by(
            func.date(Detection.created_at)
        ).order_by(
            func.count(Detection.id).desc()
        ).first()
        
        stats = {
            "total_detections": total_detections,
            "total_objects_detected": total_objects,
            "average_objects_per_detection": round(total_objects / total_detections, 2) if total_detections > 0 else 0,
            "class_distribution": class_counts,
            "most_detected_class": max(class_counts.items(), key=lambda x: x[1])[0] if class_counts else None,
            "recent_activity": {
                "detections_last_30_days": recent_detections,
                "most_active_day": {
                    "date": daily_counts[0].isoformat() if daily_counts else None,
                    "detection_count": daily_counts[1] if daily_counts else 0
                } if daily_counts else None
            },
            "ai_service_status": "available" if gemini_service and gemini_service.model else "unavailable"
        }
        
        return stats
        
    except Exception as e:
        print(f"❌ Statistics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate statistics")

# New endpoint for detection insights
@app.get("/api/v1/analysis/detection/{detection_id}/insights")
async def get_detection_insights(
    detection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed insights for a specific detection"""
    detection = db.query(Detection).filter(
        Detection.id == detection_id,
        Detection.user_id == current_user.id
    ).first()
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    # Parse analysis data
    analysis_data = {}
    if detection.analysis_data:
        try:
            analysis_data = json.loads(detection.analysis_data) if isinstance(detection.analysis_data, str) else detection.analysis_data
        except:
            analysis_data = {"error": "Could not parse analysis data"}
    
    # Get object confidence statistics
    objects = detection.objects
    confidence_scores = [obj.confidence for obj in objects]
    
    insights = {
        "detection_id": detection.id,
        "detection_name": detection.name,
        "image_dimensions": {
            "width": detection.image_width,
            "height": detection.image_height
        },
        "object_statistics": {
            "total_objects": len(objects),
            "average_confidence": round(sum(confidence_scores) / len(confidence_scores), 3) if confidence_scores else 0,
            "high_confidence_objects": len([c for c in confidence_scores if c > 0.7]),
            "medium_confidence_objects": len([c for c in confidence_scores if 0.3 <= c <= 0.7]),
            "low_confidence_objects": len([c for c in confidence_scores if c < 0.3])
        },
        "analysis_data": analysis_data,
        "created_at": detection.created_at.isoformat()
    }
    
    return insights

# New endpoint for AI service status
@app.get("/api/v1/analysis/status")
async def get_ai_service_status():
    """Get the status of AI services"""
    yolo_status = "available" if yolo_service else "unavailable"
    gemini_status = "available" if gemini_service and gemini_service.model else "unavailable"
    
    return {
        "services": {
            "object_detection": yolo_status,
            "ai_analysis": gemini_status
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# HEALTH CHECK & ROOT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "operational",
            "yolo": "operational",
            "gemini": "operational" if gemini_service else "not configured"
        }
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500
        }
    )

# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    print(f"🤖 YOLO Model: {settings.YOLO_MODEL}")
    print(f"✨ Gemini API: {'configured' if settings.GEMINI_API_KEY else 'not configured'}")
    
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
    """Run on application shutdown"""
    print(f"👋 {settings.APP_NAME} shutting down...")

# ============================================================================
# RUN APPLICATION (for development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.DEBUG else False
    )