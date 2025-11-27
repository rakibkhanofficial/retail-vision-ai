from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import json
import aiofiles
from pathlib import Path
from datetime import datetime
from PIL import Image

from app.db.session import get_db
from app.models.user import User
from app.models.detection import Detection, DetectedObject
from app.models.product import ProductPosition
from app.schemas.detection import DetectionResponse
from app.core.config import settings
from app.api.deps import get_current_user
from app.services.analysis_service import AnalysisService

router = APIRouter()

# Initialize analysis service
try:
    analysis_service = AnalysisService()
    print("✅ Analysis service initialized successfully")
except Exception as e:
    print(f"❌ Analysis service initialization failed: {e}")
    analysis_service = None

@router.post("/detections", response_model=DetectionResponse, status_code=status.HTTP_201_CREATED)
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
    
    if not analysis_service:
        raise HTTPException(
            status_code=503,
            detail="Analysis service is not available. Please try again later."
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
    
    # Run complete analysis pipeline
    try:
        print("🔄 Starting image analysis pipeline...")
        analysis_result = analysis_service.analyze_image(original_path, annotated_path)
        
        detections = analysis_result["detections"]
        analysis = analysis_result["analysis"]
        retail_analysis = analysis_result["retail_analysis"]
        
        # Create thumbnail
        analysis_service.yolo_service.create_thumbnail(annotated_path, thumbnail_path)
        
        # Get image dimensions
        img = Image.open(original_path)
        img_width, img_height = img.size
        
        print("✅ Image analysis completed successfully")
        
    except Exception as e:
        # Cleanup files
        for path in [original_path, annotated_path, thumbnail_path]:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
    
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
    
    # Save product positions
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

@router.get("/detections", response_model=List[DetectionResponse])
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

@router.get("/detections/{detection_id}", response_model=DetectionResponse)
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

@router.delete("/detections/{detection_id}", status_code=status.HTTP_204_NO_CONTENT)
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
    
    db.delete(detection)
    db.commit()
    
    return None