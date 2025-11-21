from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductPositionBase(BaseModel):
    product_name: str
    brand: Optional[str] = None
    shelf_row: Optional[int] = None
    shelf_column: Optional[int] = None
    position_description: Optional[str] = None
    quantity: int = 1
    confidence: float = 0.5
    x_min: Optional[float] = None
    y_min: Optional[float] = None
    x_max: Optional[float] = None
    y_max: Optional[float] = None

class ProductPositionCreate(ProductPositionBase):
    detection_id: int

class ProductPositionResponse(ProductPositionBase):
    id: int
    detection_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True