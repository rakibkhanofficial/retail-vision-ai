from typing import Dict, Any, List
from app.services.yolo_service import YOLODetectionService
from app.services.local_model_service import LocalModelService
from app.core.config import settings

class AnalysisService:
    """Main analysis service coordinating YOLO and Local AI Models"""
    
    def __init__(self):
        # Initialize YOLO service
        try:
            self.yolo_service = YOLODetectionService()
            print("✅ YOLO service initialized successfully")
        except Exception as e:
            print(f"❌ YOLO service initialization failed: {e}")
            self.yolo_service = None
        
        # Initialize Local Model service
        try:
            self.local_model_service = LocalModelService()
            print("✅ Local model service initialized successfully")
        except Exception as e:
            print(f"❌ Local model service initialization failed: {e}")
            self.local_model_service = None
    
    def analyze_image(self, image_path: str, output_path: str) -> Dict[str, Any]:
        """Complete image analysis pipeline with proper error handling"""
        # Check if YOLO service is available
        if not self.yolo_service:
            raise Exception("YOLO detection service is not available")
        
        # Run YOLO detection
        detections, yolo_analysis = self.yolo_service.detect_objects(image_path, output_path)
        
        # Initialize retail analysis with default structure
        retail_analysis = {
            "brands_detected": [],
            "product_categories": [],
            "positioning_analysis": "Local AI analysis not available",
            "recommendations": [],
            "shelf_organization": "",
            "stock_levels": "",
            "positioning_details": []
        }
        
        # Run Local Model analysis if available
        if self.local_model_service:
            try:
                print("🔄 Running Local AI retail analysis...")
                retail_analysis = self.local_model_service.analyze_retail_products(
                    output_path, detections, yolo_analysis
                )
                
                # Ensure retail_analysis is always a proper dictionary
                if not isinstance(retail_analysis, dict):
                    print("⚠️ Local model returned non-dict result, using fallback")
                    retail_analysis = {
                        "brands_detected": [],
                        "product_categories": [],
                        "positioning_analysis": "Analysis returned invalid format",
                        "recommendations": [],
                        "shelf_organization": "",
                        "stock_levels": "",
                        "positioning_details": []
                    }
                else:
                    print("✅ Local AI analysis completed successfully")
                
            except Exception as e:
                print(f"❌ Local AI analysis error: {e}")
                retail_analysis = {
                    "brands_detected": [],
                    "product_categories": [],
                    "positioning_analysis": f"Local analysis failed: {str(e)}",
                    "recommendations": ["AI service temporarily unavailable"],
                    "shelf_organization": "",
                    "stock_levels": "",
                    "positioning_details": []
                }
        else:
            print("ℹ️ Local model service not available, using YOLO analysis only")
            # Enhance YOLO analysis with basic retail insights
            retail_analysis = self._enhance_yolo_analysis(yolo_analysis, detections)
        
        # Merge analyses
        if not isinstance(yolo_analysis, dict):
            yolo_analysis = {}
        
        yolo_analysis["retail_analysis"] = retail_analysis
        
        # Add detection statistics
        if self.yolo_service:
            yolo_analysis["detection_statistics"] = self.yolo_service.get_detection_statistics(detections)
        
        return {
            "detections": detections,
            "analysis": yolo_analysis,
            "retail_analysis": retail_analysis
        }

    def _enhance_yolo_analysis(self, yolo_analysis: Dict[str, Any], detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance YOLO analysis with basic retail insights when local models are unavailable"""
        beverage_count = yolo_analysis.get("beverage_objects", 0)
        total_objects = yolo_analysis.get("total_objects", 0)
        
        # Basic recommendations based on YOLO data
        recommendations = []
        if total_objects == 0:
            recommendations.append("Refrigerator appears empty - consider restocking")
        elif beverage_count == 0:
            recommendations.append("No beverage products detected - check product types")
        elif total_objects < 10:
            recommendations.append("Low product density - opportunity to add more items")
        
        # Basic stock level assessment
        if total_objects == 0:
            stock_levels = "Empty"
        elif total_objects < 5:
            stock_levels = "Very low stock"
        elif total_objects < 15:
            stock_levels = "Low stock"
        elif total_objects < 30:
            stock_levels = "Moderately stocked"
        else:
            stock_levels = "Well stocked"
        
        return {
            "brands_detected": [],
            "product_categories": ["beverages" if beverage_count > 0 else "general"],
            "positioning_analysis": f"Basic analysis: {yolo_analysis.get('shelf_analysis', 'No detailed analysis')}",
            "recommendations": recommendations,
            "shelf_organization": yolo_analysis.get('shelf_analysis', 'Unknown'),
            "stock_levels": stock_levels,
            "positioning_details": self._generate_basic_positioning(detections, yolo_analysis)
        }
    
    def _generate_basic_positioning(self, detections: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate basic positioning details from YOLO data"""
        positioning_details = []
        image_dims = analysis.get("image_dimensions", {"width": 640, "height": 480})
        img_width = image_dims.get("width", 640)
        img_height = image_dims.get("height", 480)
        
        for i, det in enumerate(detections):
            center_y = det.get("center_y", 0)
            
            # Determine shelf row
            shelf_height = img_height / 3
            if center_y < shelf_height:
                shelf_row = 1
            elif center_y < 2 * shelf_height:
                shelf_row = 2
            else:
                shelf_row = 3
            
            positioning_details.append({
                "name": det["class_name"],
                "brand": "Unknown",
                "row": shelf_row,
                "column": "center",  # Basic approximation
                "description": f"{det['class_name']} on shelf {shelf_row}",
                "confidence": det["confidence"],
                "quantity": 1,
                "x_min": det.get("x_min", 0),
                "y_min": det.get("y_min", 0),
                "x_max": det.get("x_max", 0),
                "y_max": det.get("y_max", 0)
            })
        
        return positioning_details

    def answer_question(self, question: str, detection: Any, objects: List[Dict[str, Any]]) -> str:
        """Answer questions using local models or fallback to YOLO analysis"""
        if self.local_model_service:
            try:
                return self.local_model_service.answer_question(question, detection, objects)
            except Exception as e:
                print(f"❌ Local model Q&A error: {e}")
                # Fall back to basic analysis
                return self._answer_with_basic_analysis(question, objects)
        else:
            return self._answer_with_basic_analysis(question, objects)
    
    def _answer_with_basic_analysis(self, question: str, objects: List[Dict[str, Any]]) -> str:
        """Basic question answering using YOLO detection data"""
        question_lower = question.lower()
        total_objects = len(objects)
        
        if any(word in question_lower for word in ['how many', 'count', 'number']):
            class_summary = {}
            for obj in objects:
                class_name = obj['class_name']
                class_summary[class_name] = class_summary.get(class_name, 0) + 1
            
            if 'total' in question_lower:
                return f"I detected {total_objects} objects in total."
            else:
                # Try to find specific class in question
                for class_name in class_summary:
                    if class_name.lower() in question_lower:
                        return f"I detected {class_summary[class_name]} {class_name} objects."
                return f"I detected {total_objects} objects across {len(class_summary)} categories."
        
        elif any(word in question_lower for word in ['what', 'detect']):
            classes = list(set(obj['class_name'] for obj in objects))
            if classes:
                return f"I detected: {', '.join(classes)}"
            else:
                return "No objects were detected in this image."
        
        else:
            return "I can provide basic information about detected objects. For detailed analysis, please check the detection results page."

    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of all analysis services"""
        return {
            "yolo_service": "available" if self.yolo_service else "unavailable",
            "local_model_service": "available" if self.local_model_service else "unavailable",
            "overall_status": "fully_operational" if self.yolo_service and self.local_model_service 
                            else "partial" if self.yolo_service 
                            else "unavailable"
        }