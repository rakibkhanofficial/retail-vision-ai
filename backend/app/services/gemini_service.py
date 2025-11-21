import google.generativeai as genai
import json
import os
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.models.detection import Detection

class GeminiAnalysisService:
    """Gemini AI Service for Retail Product Analysis"""
    
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
    
    def analyze_retail_products(self, image_path: str, detections: List[Dict[str, Any]], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze detected objects for retail-specific insights
        (brand detection, product positioning, shelf organization)
        """
        if not self.model:
            return {
                "brands_detected": [],
                "product_categories": [],
                "positioning_analysis": "Gemini API key not configured",
                "recommendations": [],
                "shelf_organization": "",
                "stock_levels": "",
                "positioning_details": []
            }
        
        # Prepare context for Gemini
        context = self._prepare_retail_context(detections, analysis_data)
        
        # Check if image exists
        if not os.path.exists(image_path):
            return self._get_fallback_analysis("Image file not found")
        
        try:
            # Read image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            prompt = f"""You are a retail product analyst AI. Analyze this refrigerator/cooler image.

DETECTED OBJECTS DATA:
{context}

Please provide a detailed JSON analysis with:
1. "brands_detected": List of brand names you can identify
2. "product_categories": Categories of products (beverages, snacks, dairy, etc.)
3. "shelf_organization": Description of how products are organized by row/shelf
4. "positioning_details": Detailed position of each identifiable product with row and column
5. "stock_levels": Assessment of stock levels (well-stocked, low stock, empty spaces)
6. "recommendations": Suggestions for better product placement or restocking

Return ONLY valid JSON, no other text."""
            
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_data}
            ])
            
            # Parse JSON response
            response_text = response.text
            # Remove markdown code blocks if present
            response_text = response_text.replace('```json\n', '').replace('\n```', '').strip()
            
            result = json.loads(response_text)
            
            # Ensure all required fields are present
            return self._validate_analysis_result(result)
            
        except json.JSONDecodeError as e:
            print(f"Gemini JSON parsing error: {e}")
            print(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
            return self._get_fallback_analysis(f"Failed to parse AI response: {str(e)}")
            
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            return self._get_fallback_analysis(f"AI service error: {str(e)}")
    
    def answer_question(self, question: str, detection: Detection, objects: List[Dict[str, Any]]) -> str:
        """Answer questions about the detection"""
        if not self.model:
            return "Gemini API key not configured. Please add GEMINI_API_KEY to environment variables."
        
        # Prepare context
        context = self._prepare_qa_context(detection, objects)
        
        # Read annotated image
        image_path = f"/app{detection.annotated_image}"
        
        try:
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                prompt = f"""You are a retail product analysis assistant.

DETECTION CONTEXT:
{context}

USER QUESTION: {question}

Provide a clear, helpful answer based on the detection data and image."""
                
                response = self.model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": image_data}
                ])
                
                return response.text
            else:
                # Fallback to text-only if image not found
                return self._answer_question_text_only(question, context)
                
        except Exception as e:
            # Fallback to text-only on any error
            return self._answer_question_text_only(question, context, str(e))
    
    def _answer_question_text_only(self, question: str, context: str, error_msg: str = "") -> str:
        """Fallback text-only question answering"""
        try:
            prompt = f"""You are a retail product analysis assistant.

DETECTION CONTEXT:
{context}

USER QUESTION: {question}

Provide a clear, helpful answer based on the detection data."""
            
            if error_msg:
                prompt += f"\n\nNote: Image analysis failed due to: {error_msg}"
                
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e2:
            return f"Error generating answer: {str(e2)}"
    
    def _prepare_retail_context(self, detections: List[Dict[str, Any]], analysis_data: Dict[str, Any]) -> str:
        """Prepare context for retail analysis"""
        context = f"Total objects detected: {len(detections)}\n"
        context += f"Layout: {analysis_data.get('layout_type', 'unknown')}\n"
        context += f"Estimated rows: {analysis_data.get('estimated_rows', 'unknown')}\n"
        context += f"Estimated columns: {analysis_data.get('estimated_columns', 'unknown')}\n\n"
        
        context += "Detected objects by class:\n"
        for class_name, count in analysis_data.get('class_distribution', {}).items():
            context += f"  - {class_name}: {count}\n"
        
        context += "\nObject positions:\n"
        for i, det in enumerate(detections, 1):
            context += f"{i}. {det['class_name']} at ({det['center_x']:.0f}, {det['center_y']:.0f}), "
            context += f"confidence: {det['confidence']:.2%}\n"
        
        return context
    
    def _prepare_qa_context(self, detection: Detection, objects: List[Dict[str, Any]]) -> str:
        """Prepare context for Q&A"""
        context = f"Image: {detection.name or 'Unnamed'}\n"
        context += f"Total objects: {detection.total_objects}\n\n"
        
        if detection.analysis_data:
            try:
                analysis = json.loads(detection.analysis_data) if isinstance(detection.analysis_data, str) else detection.analysis_data
                context += f"Layout type: {analysis.get('layout_type', 'unknown')}\n"
                context += f"Rows: {analysis.get('estimated_rows', 'unknown')}\n"
                context += f"Columns: {analysis.get('estimated_columns', 'unknown')}\n\n"
            except:
                pass
        
        context += "Detected objects:\n"
        for obj in objects:
            context += f"  - {obj['class_name']} (confidence: {obj['confidence']:.2%})\n"
        
        if detection.products:
            context += "\nProduct positions:\n"
            for product in detection.products:
                context += f"  - {product.product_name}"
                if product.brand:
                    context += f" ({product.brand})"
                if product.shelf_row and product.shelf_column:
                    context += f" - Row {product.shelf_row}, Column {product.shelf_column}"
                context += f" - {product.quantity} unit(s)\n"
        
        return context
    
    def _validate_analysis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure the analysis result has all required fields"""
        required_fields = {
            "brands_detected": [],
            "product_categories": [],
            "positioning_analysis": "",
            "recommendations": [],
            "shelf_organization": "",
            "stock_levels": "",
            "positioning_details": []
        }
        
        # Update with actual result data, fallback to defaults if missing
        for field, default_value in required_fields.items():
            if field not in result or result[field] is None:
                result[field] = default_value
        
        return result
    
    def _get_fallback_analysis(self, error_message: str) -> Dict[str, Any]:
        """Return a proper fallback analysis structure when Gemini fails"""
        return {
            "brands_detected": [],
            "product_categories": [],
            "positioning_analysis": f"Analysis unavailable: {error_message}",
            "recommendations": ["Please check your Gemini API quota and billing settings"],
            "shelf_organization": "Unable to analyze shelf organization",
            "stock_levels": "Unable to assess stock levels",
            "positioning_details": []
        }