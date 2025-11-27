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
            
            # Define beverage-related classes for better retail analysis
            self.beverage_classes = {
                'bottle', 'can', 'cup', 'glass', 'wine glass', 
                'vase', 'container', 'pack', 'box'
            }
            
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
                    
                    # Skip if confidence is too low
                    if confidence < 0.1:  # Additional threshold
                        continue
                    
                    # Calculate additional metrics
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    width = x2 - x1
                    height = y2 - y1
                    area = width * height
                    
                    # Normalize coordinates for analysis
                    norm_center_x = center_x / img_width
                    norm_center_y = center_y / img_height
                    norm_area = area / (img_width * img_height)
                    
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
                        "area": float(area),
                        "normalized_center_x": float(norm_center_x),
                        "normalized_center_y": float(norm_center_y),
                        "normalized_area": float(norm_area)
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
        # Use predefined colors for better visualization
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green  
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Cyan
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Yellow
            (128, 0, 0),    # Maroon
            (0, 128, 0),    # Dark Green
            (0, 0, 128),    # Navy
            (128, 128, 0),  # Olive
        ]
        return colors[class_id % len(colors)]
    
    def _analyze_retail_layout(self, detections: List[Dict[str, Any]], img_width: int, img_height: int) -> Dict[str, Any]:
        """Enhanced retail layout analysis for beverage refrigerators"""
        if not detections:
            return {
                "total_objects": 0,
                "layout_type": "empty",
                "estimated_rows": 0,
                "estimated_columns": 0,
                "density": 0.0,
                "class_distribution": {},
                "avg_confidence": 0.0,
                "image_dimensions": {"width": img_width, "height": img_height},
                "beverage_objects": 0,
                "shelf_analysis": "No products detected"
            }
        
        # Filter beverage-related objects
        beverage_objects = [
            d for d in detections 
            if any(beverage_term in d["class_name"].lower() 
                  for beverage_term in ['bottle', 'can', 'cup', 'glass', 'drink', 'container'])
        ]
        
        # Enhanced row and column estimation
        rows = self._estimate_shelves(detections, img_height)
        columns = self._estimate_columns_enhanced(detections, img_width)
        
        # Calculate density metrics
        total_object_area = sum(d["area"] for d in detections)
        image_area = img_width * img_height
        density = total_object_area / image_area if image_area > 0 else 0
        
        # Object statistics by class
        class_counts = {}
        confidence_scores = []
        
        for d in detections:
            class_name = d["class_name"]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            confidence_scores.append(d["confidence"])
        
        # Determine layout type based on beverage density
        beverage_count = len(beverage_objects)
        beverage_ratio = beverage_count / len(detections) if detections else 0
        
        if beverage_count == 0:
            layout_type = "non_beverage"
        elif beverage_ratio > 0.7:
            layout_type = "beverage_dominant"
        elif beverage_ratio > 0.3:
            layout_type = "mixed_beverage"
        else:
            layout_type = "general_retail"
        
        # Shelf organization analysis
        shelf_analysis = self._analyze_shelf_organization(detections, img_height)
        
        return {
            "total_objects": len(detections),
            "beverage_objects": beverage_count,
            "beverage_ratio": round(beverage_ratio, 3),
            "layout_type": layout_type,
            "estimated_rows": rows,
            "estimated_columns": columns,
            "density": round(density, 4),
            "class_distribution": class_counts,
            "avg_confidence": round(sum(confidence_scores) / len(confidence_scores), 4),
            "image_dimensions": {"width": img_width, "height": img_height},
            "shelf_analysis": shelf_analysis,
            "detection_summary": f"Found {len(detections)} objects ({beverage_count} beverage-related)"
        }
    
    def _estimate_shelves(self, detections: List[Dict[str, Any]], img_height: int) -> int:
        """Enhanced shelf estimation using clustering"""
        if len(detections) < 2:
            return max(1, len(detections))
        
        # Use normalized y positions for clustering
        y_positions = [d["normalized_center_y"] for d in detections]
        y_sorted = sorted(y_positions)
        
        # Simple clustering based on gaps
        clusters = []
        current_cluster = [y_sorted[0]]
        
        for i in range(1, len(y_sorted)):
            gap = y_sorted[i] - y_sorted[i-1]
            # If gap is significant, start new cluster
            if gap > 0.1:  # 10% of image height
                clusters.append(current_cluster)
                current_cluster = [y_sorted[i]]
            else:
                current_cluster.append(y_sorted[i])
        
        clusters.append(current_cluster)
        
        return len(clusters)
    
    def _estimate_columns_enhanced(self, detections: List[Dict[str, Any]], img_width: int) -> int:
        """Enhanced column estimation"""
        if len(detections) < 2:
            return max(1, len(detections))
        
        x_positions = [d["normalized_center_x"] for d in detections]
        x_sorted = sorted(x_positions)
        
        # Simple clustering based on gaps
        clusters = []
        current_cluster = [x_sorted[0]]
        
        for i in range(1, len(x_sorted)):
            gap = x_sorted[i] - x_sorted[i-1]
            # If gap is significant, start new cluster
            if gap > 0.15:  # 15% of image width
                clusters.append(current_cluster)
                current_cluster = [x_sorted[i]]
            else:
                current_cluster.append(x_sorted[i])
        
        clusters.append(current_cluster)
        
        return len(clusters)
    
    def _analyze_shelf_organization(self, detections: List[Dict[str, Any]], img_height: int) -> str:
        """Analyze how objects are organized on shelves"""
        if not detections:
            return "No objects to analyze"
        
        # Define shelf regions
        shelf_height = img_height / 3
        top_shelf = [d for d in detections if d["center_y"] < shelf_height]
        middle_shelf = [d for d in detections if shelf_height <= d["center_y"] < 2 * shelf_height]
        bottom_shelf = [d for d in detections if d["center_y"] >= 2 * shelf_height]
        
        shelf_counts = {
            "top": len(top_shelf),
            "middle": len(middle_shelf),
            "bottom": len(bottom_shelf)
        }
        
        # Find most populated shelf
        most_populated = max(shelf_counts.items(), key=lambda x: x[1])
        
        if most_populated[1] == 0:
            return "Objects randomly distributed"
        
        # Analyze distribution
        total = len(detections)
        top_percent = shelf_counts["top"] / total * 100
        middle_percent = shelf_counts["middle"] / total * 100
        bottom_percent = shelf_counts["bottom"] / total * 100
        
        if max(top_percent, middle_percent, bottom_percent) > 60:
            return f"Concentrated on {most_populated[0]} shelf ({most_populated[1]} items)"
        elif abs(top_percent - middle_percent) < 20 and abs(middle_percent - bottom_percent) < 20:
            return "Evenly distributed across shelves"
        else:
            return f"Uneven distribution: Top {shelf_counts['top']}, Middle {shelf_counts['middle']}, Bottom {shelf_counts['bottom']}"
    
    def create_thumbnail(self, image_path: str, thumbnail_path: str, size: tuple = (300, 300)):
        """Create a thumbnail of the image"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            
            img = Image.open(image_path)
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, "JPEG", quality=85)
            print(f"✅ Thumbnail created: {thumbnail_path}")
        except Exception as e:
            print(f"❌ Thumbnail creation error: {e}")
            # Create a fallback thumbnail
            self._create_fallback_thumbnail(thumbnail_path, size)
    
    def _create_fallback_thumbnail(self, thumbnail_path: str, size: tuple = (300, 300)):
        """Create a simple fallback thumbnail when original fails"""
        try:
            # Create a simple colored image with error message
            img = Image.new('RGB', size, color=(240, 240, 240))
            img.save(thumbnail_path, "JPEG", quality=85)
            print(f"✅ Fallback thumbnail created: {thumbnail_path}")
        except Exception as e:
            print(f"❌ Fallback thumbnail also failed: {e}")
    
    def get_detection_statistics(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get detailed statistics about detections"""
        if not detections:
            return {"error": "No detections available"}
        
        # Confidence statistics
        confidences = [d["confidence"] for d in detections]
        
        # Size statistics
        areas = [d["area"] for d in detections]
        widths = [d["width"] for d in detections]
        heights = [d["height"] for d in detections]
        
        return {
            "total_detections": len(detections),
            "confidence_stats": {
                "average": round(sum(confidences) / len(confidences), 4),
                "max": round(max(confidences), 4),
                "min": round(min(confidences), 4),
                "high_confidence": len([c for c in confidences if c > 0.7]),
                "medium_confidence": len([c for c in confidences if 0.3 <= c <= 0.7]),
                "low_confidence": len([c for c in confidences if c < 0.3])
            },
            "size_stats": {
                "average_area": round(sum(areas) / len(areas), 2),
                "average_width": round(sum(widths) / len(widths), 2),
                "average_height": round(sum(heights) / len(heights), 2),
                "largest_object": max(areas) if areas else 0,
                "smallest_object": min(areas) if areas else 0
            }
        }