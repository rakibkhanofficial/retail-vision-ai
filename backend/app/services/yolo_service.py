import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
from typing import List, Dict, Any, Tuple
import os
import torch
from app.core.config import settings

class YOLODetectionService:
    """YOLO Object Detection Service with Retail-Specific Analysis"""
    
    def __init__(self):
        # Set environment variable to handle PyTorch weights_only issue
        os.environ['TORCH_WEIGHTS_ONLY'] = '0'
        
        try:
            # Try to load with the specific model path
            model_path = settings.YOLO_MODEL
            if not os.path.exists(model_path):
                print(f"📥 Downloading YOLO model: {model_path}")
                # This will download the model automatically
                self.model = YOLO(model_path)
            else:
                print(f"✅ Loading existing YOLO model: {model_path}")
                self.model = YOLO(model_path)
                
            self.model.conf = settings.CONFIDENCE_THRESHOLD
            self.model.iou = settings.IOU_THRESHOLD
            print("✅ YOLO model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            print("🔄 Attempting to download model again...")
            try:
                # Force download
                self.model = YOLO(model_path, verbose=True)
                self.model.conf = settings.CONFIDENCE_THRESHOLD
                self.model.iou = settings.IOU_THRESHOLD
                print("✅ YOLO model downloaded and loaded successfully!")
            except Exception as e2:
                print(f"❌ Failed to load YOLO model: {e2}")
                raise e2
    
    def detect_objects(self, image_path: str, output_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Detect objects in an image and return detailed results
        
        Returns:
            Tuple of (detections_list, analysis_dict)
        """
        try:
            # Run detection
            results = self.model(image_path)[0]
            
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image from {image_path}")
                
            img_height, img_width = img.shape[:2]
            
            detections = []
            boxes = results.boxes
            
            if boxes is not None and len(boxes) > 0:
                # Process each detection
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    
                    # Calculate additional metrics
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    width = x2 - x1
                    height = y2 - y1
                    area = width * height
                    
                    # Draw bounding box
                    color = self._get_color(class_id)
                    cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 3)
                    
                    # Draw label background
                    label = f"{class_name}: {confidence:.2%}"
                    (label_w, label_h), baseline = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                    )
                    cv2.rectangle(
                        img,
                        (int(x1), int(y1) - label_h - baseline - 10),
                        (int(x1) + label_w, int(y1)),
                        color,
                        -1
                    )
                    
                    # Draw label text
                    cv2.putText(
                        img, label,
                        (int(x1), int(y1) - baseline - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2
                    )
                    
                    # Add detection to list
                    detections.append({
                        "class_name": class_name,
                        "confidence": confidence,
                        "x_min": float(x1),
                        "y_min": float(y1),
                        "x_max": float(x2),
                        "y_max": float(y2),
                        "center_x": float(center_x),
                        "center_y": float(center_y),
                        "width": float(width),
                        "height": float(height),
                        "area": float(area)
                    })
            
            # Save annotated image
            cv2.imwrite(output_path, img)
            
            # Perform retail-specific analysis
            analysis = self._analyze_retail_layout(detections, img_width, img_height)
            
            return detections, analysis
            
        except Exception as e:
            print(f"❌ Detection error: {e}")
            raise e
    
    def _get_color(self, class_id: int) -> tuple:
        """Get consistent color for class"""
        np.random.seed(class_id)
        return tuple(map(int, np.random.randint(0, 255, 3)))
    
    def _analyze_retail_layout(self, detections: List[Dict[str, Any]], img_width: int, img_height: int) -> Dict[str, Any]:
        """Analyze retail-specific layout (shelves, rows, columns)"""
        if not detections:
            return {
                "total_objects": 0,
                "layout_type": "empty",
                "rows": 0,
                "columns": 0,
                "density": 0.0
            }
        
        # Group objects by vertical position (rows)
        y_positions = [d["center_y"] for d in detections]
        y_sorted = sorted(y_positions)
        
        # Estimate number of rows (using clustering approach)
        rows = self._estimate_rows(y_sorted, img_height)
        
        # Group objects by horizontal position (columns)
        x_positions = [d["center_x"] for d in detections]
        x_sorted = sorted(x_positions)
        
        # Estimate number of columns
        columns = self._estimate_columns(x_sorted, img_width)
        
        # Calculate density
        total_object_area = sum(d["area"] for d in detections)
        image_area = img_width * img_height
        density = total_object_area / image_area if image_area > 0 else 0
        
        # Classify layout type
        if len(detections) > 20:
            layout_type = "dense_retail"
        elif len(detections) > 10:
            layout_type = "retail_shelf"
        elif len(detections) > 5:
            layout_type = "sparse_display"
        else:
            layout_type = "minimal"
        
        # Object statistics by class
        class_counts = {}
        for d in detections:
            class_name = d["class_name"]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        return {
            "total_objects": len(detections),
            "layout_type": layout_type,
            "estimated_rows": rows,
            "estimated_columns": columns,
            "density": round(density, 4),
            "class_distribution": class_counts,
            "avg_confidence": round(sum(d["confidence"] for d in detections) / len(detections), 4),
            "image_dimensions": {"width": img_width, "height": img_height}
        }
    
    def _estimate_rows(self, y_positions: List[float], img_height: int) -> int:
        """Estimate number of rows using gap detection"""
        if len(y_positions) < 2:
            return 1
        
        # Calculate gaps between consecutive y positions
        gaps = []
        for i in range(1, len(y_positions)):
            gap = y_positions[i] - y_positions[i-1]
            gaps.append(gap)
        
        # Find significant gaps (larger than average + std)
        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            std_gap = (sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)) ** 0.5
            threshold = avg_gap + std_gap
            
            significant_gaps = [g for g in gaps if g > threshold]
            return len(significant_gaps) + 1
        
        return 1
    
    def _estimate_columns(self, x_positions: List[float], img_width: int) -> int:
        """Estimate number of columns using gap detection"""
        if len(x_positions) < 2:
            return 1
        
        gaps = []
        for i in range(1, len(x_positions)):
            gap = x_positions[i] - x_positions[i-1]
            gaps.append(gap)
        
        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            std_gap = (sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)) ** 0.5
            threshold = avg_gap + std_gap
            
            significant_gaps = [g for g in gaps if g > threshold]
            return len(significant_gaps) + 1
        
        return 1
    
    def create_thumbnail(self, image_path: str, thumbnail_path: str, size: tuple = (300, 300)):
        """Create a thumbnail of the image"""
        try:
            img = Image.open(image_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, "JPEG", quality=85)
        except Exception as e:
            print(f"❌ Thumbnail creation error: {e}")
            raise e