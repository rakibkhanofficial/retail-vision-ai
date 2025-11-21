from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.product import ProductPositionResponse

class DetectedObjectBase(BaseModel):
    class_name: str
    confidence: float
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    center_x: Optional[float] = None
    center_y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    area: Optional[float] = None

class DetectionBase(BaseModel):
    name: Optional[str] = None

class DetectionCreate(DetectionBase):
    pass

class DetectionResponse(DetectionBase):
    id: int
    user_id: int
    original_image: str
    annotated_image: str
    thumbnail: str
    image_width: int
    image_height: int
    total_objects: int
    analysis_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    objects: List[DetectedObjectBase] = []
    products: List[ProductPositionResponse] = []
    
    class Config:
        from_attributes = True

class QuestionRequest(BaseModel):
    detection_id: int
    question: str

class QuestionResponse(BaseModel):
    answer: str
    detection_id: int