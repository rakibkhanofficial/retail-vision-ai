import torch
import cv2
import numpy as np
from PIL import Image
import json
import os
from typing import List, Dict, Any, Optional
from transformers import (
    BlipProcessor, 
    BlipForConditionalGeneration,
    CLIPProcessor, 
    CLIPModel
)
import torch.nn.functional as F

class LocalModelService:
    """Local model service for beverage refrigerator analysis"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🚀 Using device: {self.device}")
        
        # Initialize models
        self.blip_processor = None
        self.blip_model = None
        self.clip_processor = None
        self.clip_model = None
        
        self._load_models()
    
    def _load_models(self):
        """Load all local models"""
        try:
            # Load BLIP for image understanding (smaller, faster)
            print("📥 Loading BLIP model...")
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-base"
            ).to(self.device)
            print("✅ BLIP loaded successfully")
            
            # Load CLIP for brand recognition
            print("📥 Loading CLIP model...")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
            print("✅ CLIP loaded successfully")
            
            # Beverage brands for classification
            self.beverage_brands = [
                "Coca-Cola", "Pepsi", "Sprite", "Fanta", "Mountain Dew",
                "Red Bull", "Monster", "Gatorade", "Aquafina", "Dasani",
                "Dr Pepper", "7UP", "Mirinda", "Schweppes", "Lipton",
                "Nestea", "Starbucks", "Budweiser", "Heineken", "Corona",
                "bottle", "can", "beverage", "drink"
            ]
            
        except Exception as e:
            print(f"❌ Model loading error: {e}")
    
    def analyze_retail_products(self, image_path: str, detections: List[Dict[str, Any]], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze refrigerator image using local models
        """
        if not os.path.exists(image_path):
            return self._get_fallback_analysis("Image file not found")
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Analyze with BLIP
            blip_analysis = self._analyze_with_blip(image)
            
            # Detect brands with CLIP
            brand_analysis = self._detect_brands_with_clip(image, detections)
            
            # Analyze shelf organization
            shelf_analysis = self._analyze_shelf_organization(detections, analysis_data)
            
            # Generate positioning details
            positioning_details = self._generate_positioning_details(detections, analysis_data)
            
            # Combine all analyses
            result = {
                "brands_detected": brand_analysis.get("detected_brands", []),
                "product_categories": blip_analysis.get("categories", ["beverages"]),
                "positioning_analysis": shelf_analysis.get("analysis", ""),
                "recommendations": self._generate_recommendations(detections, brand_analysis),
                "shelf_organization": shelf_analysis.get("organization", ""),
                "stock_levels": self._assess_stock_levels(detections),
                "positioning_details": positioning_details,
                "overall_analysis": blip_analysis.get("description", "")
            }
            
            return self._validate_analysis_result(result)
            
        except Exception as e:
            print(f"❌ Local model analysis error: {e}")
            return self._get_fallback_analysis(f"Analysis error: {str(e)}")
    
    def _analyze_with_blip(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze image using BLIP"""
        if not self.blip_model:
            return {"description": "BLIP model not available", "categories": ["beverages"]}
        
        try:
            # Get general description
            inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
            
            generated_ids = self.blip_model.generate(
                **inputs,
                max_length=50,
                num_beams=5,
                early_stopping=True
            )
            
            description = self.blip_processor.decode(generated_ids[0], skip_special_tokens=True)
            
            # Extract categories from description
            categories = self._extract_categories(description)
            
            return {
                "description": description,
                "categories": categories
            }
            
        except Exception as e:
            print(f"BLIP analysis error: {e}")
            return {"description": "Unable to analyze image", "categories": ["beverages"]}
    
    def _detect_brands_with_clip(self, image: Image.Image, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect beverage brands using CLIP"""
        if not self.clip_model or not detections:
            return {"detected_brands": []}
        
        try:
            # Prepare brand texts
            brand_texts = [f"a photo of {brand} drink" for brand in self.beverage_brands]
            brand_texts.extend([f"a {brand} beverage" for brand in self.beverage_brands])
            brand_texts.extend([f"{brand} logo" for brand in self.beverage_brands])
            
            # Process image and texts
            inputs = self.clip_processor(
                text=brand_texts, 
                images=image, 
                return_tensors="pt", 
                padding=True
            ).to(self.device)
            
            # Get similarity scores
            outputs = self.clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
            
            # Get top brands
            top_probs, top_indices = torch.topk(probs, 5)
            
            detected_brands = []
            for i in range(len(top_indices[0])):
                brand_idx = top_indices[0][i].item()
                prob = top_probs[0][i].item()
                
                if prob > 0.05:  # Lower confidence threshold for broader detection
                    brand_name = self.beverage_brands[brand_idx % len(self.beverage_brands)]
                    if brand_name not in [b["brand"] for b in detected_brands]:
                        detected_brands.append({
                            "brand": brand_name,
                            "confidence": round(prob, 3)
                        })
            
            return {"detected_brands": detected_brands}
            
        except Exception as e:
            print(f"CLIP brand detection error: {e}")
            return {"detected_brands": []}
    
    def _analyze_shelf_organization(self, detections: List[Dict[str, Any]], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze shelf organization based on object positions"""
        if not detections:
            return {
                "organization": "No products detected",
                "analysis": "Empty refrigerator or no products detected"
            }
        
        # Group objects by vertical position (shelves)
        image_height = analysis_data.get('image_dimensions', {}).get('height', 480)
        
        # Define shelf regions
        shelf_regions = [
            {"name": "Top Shelf", "min_y": 0, "max_y": image_height * 0.3},
            {"name": "Middle Shelf", "min_y": image_height * 0.3, "max_y": image_height * 0.7},
            {"name": "Bottom Shelf", "min_y": image_height * 0.7, "max_y": image_height}
        ]
        
        shelf_contents = {}
        for shelf in shelf_regions:
            shelf_contents[shelf["name"]] = []
        
        # Assign objects to shelves
        for det in detections:
            center_y = det.get('center_y', 0)
            for shelf in shelf_regions:
                if shelf["min_y"] <= center_y <= shelf["max_y"]:
                    shelf_contents[shelf["name"]].append(det['class_name'])
                    break
        
        # Generate analysis
        analysis = f"Detected {len(detections)} products across {len([s for s in shelf_contents.values() if s])} shelves. "
        
        # Check shelf utilization
        for shelf_name, items in shelf_contents.items():
            if items:
                unique_items = list(set(items))
                analysis += f"{shelf_name}: {len(items)} items ({', '.join(unique_items[:2])}). "
        
        return {
            "organization": json.dumps(shelf_contents),
            "analysis": analysis.strip()
        }
    
    def _generate_positioning_details(self, detections: List[Dict[str, Any]], analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed positioning information"""
        positioning_details = []
        
        image_height = analysis_data.get('image_dimensions', {}).get('height', 480)
        image_width = analysis_data.get('image_dimensions', {}).get('width', 640)
        
        # Define shelf rows
        shelf_rows = 3
        row_height = image_height / shelf_rows
        
        for i, det in enumerate(detections):
            center_y = det.get('center_y', 0)
            center_x = det.get('center_x', 0)
            
            # Determine shelf row
            shelf_row = int(center_y / row_height) + 1
            shelf_row = min(shelf_row, shelf_rows)
            
            # Determine column position
            if center_x < image_width / 3:
                column_position = "left"
            elif center_x < 2 * image_width / 3:
                column_position = "center" 
            else:
                column_position = "right"
            
            positioning_details.append({
                "name": det['class_name'],
                "brand": "Unknown",
                "row": shelf_row,
                "column": column_position,
                "description": f"{det['class_name']} on shelf {shelf_row}, {column_position} side",
                "confidence": det['confidence'],
                "quantity": 1,
                "x_min": det.get('x_min', 0),
                "y_min": det.get('y_min', 0),
                "x_max": det.get('x_max', 0),
                "y_max": det.get('y_max', 0)
            })
        
        return positioning_details
    
    def _assess_stock_levels(self, detections: List[Dict[str, Any]]) -> str:
        """Assess stock levels based on object count and distribution"""
        total_objects = len(detections)
        
        if total_objects == 0:
            return "Empty"
        elif total_objects < 5:
            return "Very low stock"
        elif total_objects < 15:
            return "Low stock"
        elif total_objects < 30:
            return "Moderately stocked"
        else:
            return "Well stocked"
    
    def _generate_recommendations(self, detections: List[Dict[str, Any]], brand_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        total_objects = len(detections)
        
        if total_objects == 0:
            recommendations.append("Refrigerator appears empty - consider restocking")
        elif total_objects < 10:
            recommendations.append("Low product density - opportunity to add more products")
        
        # Check brand variety
        detected_brands = [b["brand"] for b in brand_analysis.get("detected_brands", [])]
        if len(detected_brands) < 2 and total_objects > 5:
            recommendations.append("Limited brand variety - consider adding more brands")
        
        # Space utilization recommendations
        if total_objects > 20:
            recommendations.append("Good product density - maintain current stock levels")
        else:
            recommendations.append("Consider adding more products to optimize space utilization")
        
        return recommendations
    
    def _extract_categories(self, description: str) -> List[str]:
        """Extract product categories from description"""
        categories = []
        desc_lower = description.lower()
        
        category_keywords = {
            "soda": ["soda", "soft drink", "carbonated", "cola", "pop"],
            "energy drinks": ["energy drink", "energy", "monster", "red bull"],
            "water": ["water", "bottled water", "aquafina", "dasani"],
            "juice": ["juice", "fruit drink", "orange juice"],
            "sports drinks": ["sports drink", "gatorade", "powerade"],
            "tea": ["tea", "iced tea", "lipton", "nestea"],
            "coffee": ["coffee", "starbucks"],
            "beer": ["beer", "alcohol", "budweiser", "heineken", "corona"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                if category not in categories:
                    categories.append(category)
        
        return categories if categories else ["beverages"]
    
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
        
        for field, default_value in required_fields.items():
            if field not in result or result[field] is None:
                result[field] = default_value
        
        return result
    
    def _get_fallback_analysis(self, error_message: str) -> Dict[str, Any]:
        """Return fallback analysis when models fail"""
        return {
            "brands_detected": [],
            "product_categories": ["beverages"],
            "positioning_analysis": f"Analysis limited: {error_message}",
            "recommendations": ["Check image quality and ensure products are visible"],
            "shelf_organization": "Unable to analyze organization",
            "stock_levels": "Unknown",
            "positioning_details": []
        }

    def answer_question(self, question: str, detection: Any, objects: List[Dict[str, Any]]) -> str:
        """Answer questions about the detection using local models"""
        try:
            question_lower = question.lower()
            
            if any(word in question_lower for word in ['how many', 'count', 'number']):
                return self._answer_count_question(question, objects)
            
            elif any(word in question_lower for word in ['what', 'detect', 'see', 'find']):
                return self._answer_what_question(question, objects)
            
            elif any(word in question_lower for word in ['where', 'position', 'location']):
                return self._answer_position_question(question, objects)
            
            elif any(word in question_lower for word in ['brand', 'coca', 'pepsi', 'red bull']):
                return self._answer_brand_question(question, objects)
            
            elif any(word in question_lower for word in ['empty', 'space', 'vacant']):
                return self._answer_space_question(question, objects)
            
            else:
                return self._answer_general_question(question, objects)
                
        except Exception as e:
            return f"I encountered an error while processing your question: {str(e)}"
    
    def _answer_count_question(self, question: str, objects: List[Dict[str, Any]]) -> str:
        """Answer counting questions"""
        total_objects = len(objects)
        class_summary = {}
        
        for obj in objects:
            class_name = obj['class_name']
            class_summary[class_name] = class_summary.get(class_name, 0) + 1
        
        if 'total' in question.lower() or 'all' in question.lower():
            class_details = ", ".join([f"{count} {cls}" for cls, count in class_summary.items()])
            return f"I detected {total_objects} objects in total: {class_details}."
        
        # Count specific classes mentioned in question
        question_lower = question.lower()
        for class_name in class_summary.keys():
            if class_name.lower() in question_lower:
                count = class_summary[class_name]
                return f"I detected {count} {class_name} objects."
        
        return f"I detected {total_objects} objects in total across {len(class_summary)} different types."

    def _answer_what_question(self, question: str, objects: List[Dict[str, Any]]) -> str:
        """Answer 'what' questions"""
        if not objects:
            return "I didn't detect any objects in this image."
        
        classes = list(set(obj['class_name'] for obj in objects))
        
        if len(classes) == 1:
            return f"I detected {classes[0]} objects in this refrigerator."
        elif len(classes) <= 5:
            class_list = ", ".join(classes)
            return f"I detected the following objects: {class_list}."
        else:
            main_classes = classes[:5]
            class_list = ", ".join(main_classes)
            return f"I detected {len(classes)} types of objects including: {class_list}, and others."

    def _answer_position_question(self, question: str, objects: List[Dict[str, Any]]) -> str:
        """Answer position-related questions"""
        if not objects:
            return "No objects detected to analyze positions."
        
        # Simple position analysis based on coordinates
        image_center_x = 320  # Assuming standard image size
        left_objects = [obj for obj in objects if obj.get('center_x', 0) < image_center_x]
        right_objects = [obj for obj in objects if obj.get('center_x', 0) >= image_center_x]
        
        left_count = len(left_objects)
        right_count = len(right_objects)
        
        if 'left' in question.lower():
            left_classes = list(set(obj['class_name'] for obj in left_objects))
            return f"I found {left_count} objects on the left side: {', '.join(left_classes) if left_classes else 'none'}"
        
        elif 'right' in question.lower():
            right_classes = list(set(obj['class_name'] for obj in right_objects))
            return f"I found {right_count} objects on the right side: {', '.join(right_classes) if right_classes else 'none'}"
        
        return f"Objects are distributed with {left_count} on the left and {right_count} on the right side of the refrigerator."

    def _answer_brand_question(self, question: str, objects: List[Dict[str, Any]]) -> str:
        """Answer brand-related questions"""
        # Simple brand detection based on class names
        question_lower = question.lower()
        detected_brands = []
        
        for obj in objects:
            class_name_lower = obj['class_name'].lower()
            for brand in self.beverage_brands:
                if brand.lower() in class_name_lower and brand.lower() in question_lower:
                    detected_brands.append(brand)
        
        if detected_brands:
            unique_brands = list(set(detected_brands))
            return f"I detected {len(unique_brands)} brands including: {', '.join(unique_brands)}."
        else:
            return "I couldn't identify specific brands in this image. For detailed brand detection, please check the analysis results."

    def _answer_space_question(self, question: str, objects: List[Dict[str, Any]]) -> str:
        """Answer space-related questions"""
        total_objects = len(objects)
        
        if total_objects == 0:
            return "The refrigerator appears completely empty with plenty of space available."
        elif total_objects < 10:
            return f"With only {total_objects} items, there is significant empty space available for more products."
        elif total_objects < 25:
            return f"With {total_objects} items, there is moderate space available. Some shelves might have empty spots."
        else:
            return f"With {total_objects} items, the refrigerator is quite full. Limited space available for additional products."

    def _answer_general_question(self, question: str, objects: List[Dict[str, Any]]) -> str:
        """Answer general questions"""
        total_objects = len(objects)
        
        if total_objects == 0:
            return "The refrigerator appears to be empty based on my analysis. No products were detected."
        elif total_objects < 10:
            return f"I detected {total_objects} products. The refrigerator has low stock with plenty of space available for additional items."
        else:
            class_summary = {}
            for obj in objects:
                class_name = obj['class_name']
                class_summary[class_name] = class_summary.get(class_name, 0) + 1
            
            main_products = ", ".join([f"{count} {cls}" for cls, count in list(class_summary.items())[:3]])
            return f"The refrigerator contains {total_objects} products including {main_products}. It appears to be reasonably stocked with good product variety."