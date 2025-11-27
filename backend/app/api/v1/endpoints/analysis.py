from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, List

from app.db.session import get_db
from app.models.user import User
from app.models.detection import Detection, DetectedObject
from app.schemas.detection import QuestionRequest, QuestionResponse
from app.api.deps import get_current_user
from app.services.analysis_service import AnalysisService

router = APIRouter()

# Initialize analysis service
try:
    analysis_service = AnalysisService()
except Exception as e:
    analysis_service = None

def _generate_fallback_answer(question: str, detection: Detection, objects: List[Dict], error_msg: str = "") -> str:
    """Generate a fallback answer when AI service is unavailable"""
    question_lower = question.lower()
    
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
               (f"AI service error: {error_msg}" if error_msg else "Please check your AI model configuration.")

@router.post("/analysis/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about a detection"""
    detection = db.query(Detection).filter(
        Detection.id == request.detection_id,
        Detection.user_id == current_user.id
    ).first()
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
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
    
    if not analysis_service:
        fallback_answer = _generate_fallback_answer(request.question, detection, objects)
        return {
            "answer": fallback_answer,
            "detection_id": detection.id
        }
    
    try:
        print(f"🔍 Asking question about detection {detection.id}: {request.question}")
        answer = analysis_service.answer_question(request.question, detection, objects)
        print("✅ Question answered successfully")
        
    except Exception as e:
        print(f"❌ Question answering error: {e}")
        fallback_answer = _generate_fallback_answer(request.question, detection, objects, str(e))
        answer = fallback_answer
    
    return {
        "answer": answer,
        "detection_id": detection.id
    }

@router.get("/analysis/statistics")
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's detection statistics"""
    try:
        total_detections = db.query(Detection).filter(Detection.user_id == current_user.id).count()
        total_objects = db.query(DetectedObject).join(Detection).filter(Detection.user_id == current_user.id).count()
        
        objects = db.query(DetectedObject).join(Detection).filter(Detection.user_id == current_user.id).all()
        class_counts = {}
        for obj in objects:
            class_counts[obj.class_name] = class_counts.get(obj.class_name, 0) + 1
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_detections = db.query(Detection).filter(
            Detection.user_id == current_user.id,
            Detection.created_at >= thirty_days_ago
        ).count()
        
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
            "ai_service_status": "available" if analysis_service else "unavailable"
        }
        
        return stats
        
    except Exception as e:
        print(f"❌ Statistics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate statistics")

@router.get("/analysis/detection/{detection_id}/insights")
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
    
    analysis_data = {}
    if detection.analysis_data:
        try:
            analysis_data = json.loads(detection.analysis_data) if isinstance(detection.analysis_data, str) else detection.analysis_data
        except:
            analysis_data = {"error": "Could not parse analysis data"}
    
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

@router.get("/analysis/status")
async def get_ai_service_status():
    """Get the status of AI services"""
    service_status = "available" if analysis_service else "unavailable"
    yolo_status = "available" if analysis_service and analysis_service.yolo_service else "unavailable"
    local_model_status = "available" if analysis_service and analysis_service.local_model_service else "unavailable"
    
    return {
        "services": {
            "analysis_service": service_status,
            "object_detection": yolo_status,
            "local_ai_analysis": local_model_status
        },
        "timestamp": datetime.utcnow().isoformat()
    }