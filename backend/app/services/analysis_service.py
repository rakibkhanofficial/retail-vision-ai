from typing import Dict, Any, List
from app.services.yolo_service import YOLODetectionService
from app.services.gemini_service import GeminiAnalysisService
from app.core.config import settings

class AnalysisService:
    """Main analysis service coordinating YOLO and Gemini"""
    
    def __init__(self):
        self.yolo_service = YOLODetectionService()
        
        # Initialize Gemini service properly
        self.gemini_service = None
        if settings.GEMINI_API_KEY:
            try:
                self.gemini_service = GeminiAnalysisService()
                # Test if the service is actually working
                if not self.gemini_service.model:
                    print("⚠️ Gemini service initialized but model is not available")
                    self.gemini_service = None
                else:
                    print("✅ Gemini service initialized successfully")
            except Exception as e:
                print(f"❌ Gemini service initialization failed: {e}")
                self.gemini_service = None
    
    def analyze_image(self, image_path: str, output_path: str) -> Dict[str, Any]:
        """Complete image analysis pipeline with proper error handling"""
        # Run YOLO detection
        detections, yolo_analysis = self.yolo_service.detect_objects(image_path, output_path)
        
        # Initialize retail analysis with default structure
        retail_analysis = {
            "brands_detected": [],
            "product_categories": [],
            "positioning_analysis": "Gemini analysis not available",
            "recommendations": [],
            "shelf_organization": "",
            "stock_levels": "",
            "positioning_details": []
        }
        
        # Run Gemini analysis if available
        if self.gemini_service and self.gemini_service.model:
            try:
                print("🔄 Running Gemini retail analysis...")
                retail_analysis = self.gemini_service.analyze_retail_products(
                    output_path, detections, yolo_analysis
                )
                
                # Ensure retail_analysis is always a proper dictionary
                if not isinstance(retail_analysis, dict):
                    print("⚠️ Gemini returned non-dict result, using fallback")
                    retail_analysis = {
                        "brands_detected": [],
                        "product_categories": [],
                        "positioning_analysis": "Analysis returned invalid format",
                        "recommendations": [],
                        "shelf_organization": "",
                        "stock_levels": "",
                        "positioning_details": []
                    }
                
                print("✅ Gemini analysis completed successfully")
                
            except Exception as e:
                print(f"❌ Retail analysis error: {e}")
                retail_analysis = {
                    "brands_detected": [],
                    "product_categories": [],
                    "positioning_analysis": f"Analysis failed: {str(e)}",
                    "recommendations": ["API service temporarily unavailable"],
                    "shelf_organization": "",
                    "stock_levels": "",
                    "positioning_details": []
                }
        else:
            print("ℹ️ Gemini service not available, skipping retail analysis")
        
        # Merge analyses - ensure yolo_analysis is a dict
        if not isinstance(yolo_analysis, dict):
            yolo_analysis = {}
        
        yolo_analysis["retail_analysis"] = retail_analysis
        
        return {
            "detections": detections,
            "analysis": yolo_analysis,
            "retail_analysis": retail_analysis
        }