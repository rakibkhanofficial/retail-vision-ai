from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.detection import Detection, DetectedObject
from app.schemas.detection import QuestionRequest, QuestionResponse
from app.api.deps import get_current_user
from app.services.gemini_service import GeminiAnalysisService
from app.core.config import settings

router = APIRouter()

gemini_service = GeminiAnalysisService() if settings.GEMINI_API_KEY else None

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about a detection"""
    if not gemini_service:
        raise HTTPException(
            status_code=503,
            detail="AI analysis service not available. Please configure GEMINI_API_KEY."
        )
    
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
    
    # Get answer from Gemini
    try:
        answer = gemini_service.answer_question(request.question, detection, objects)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
    
    return {
        "answer": answer,
        "detection_id": detection.id
    }

@router.get("/statistics")
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's detection statistics"""
    total_detections = db.query(Detection).filter(Detection.user_id == current_user.id).count()
    total_objects = db.query(DetectedObject).join(Detection).filter(Detection.user_id == current_user.id).count()
    
    # Get class distribution across all detections
    objects = db.query(DetectedObject).join(Detection).filter(Detection.user_id == current_user.id).all()
    class_counts = {}
    for obj in objects:
        class_counts[obj.class_name] = class_counts.get(obj.class_name, 0) + 1
    
    return {
        "total_detections": total_detections,
        "total_objects_detected": total_objects,
        "average_objects_per_detection": round(total_objects / total_detections, 2) if total_detections > 0 else 0,
        "class_distribution": class_counts,
        "most_detected_class": max(class_counts.items(), key=lambda x: x[1])[0] if class_counts else None
    }