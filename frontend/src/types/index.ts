export interface User {
  id: number
  email: string
  username: string
  full_name: string
  is_active: boolean
  created_at: string
}

export interface Detection {
  id: number
  user_id: number
  name: string
  original_image: string
  annotated_image: string
  thumbnail: string
  image_width: number
  image_height: number
  total_objects: number
  analysis_data?: any
  created_at: string
  objects: DetectedObject[]
  products: ProductPosition[]
}

export interface DetectedObject {
  id: number
  detection_id: number
  class_name: string
  confidence: number
  x_min: number
  y_min: number
  x_max: number
  y_max: number
  center_x?: number
  center_y?: number
  width?: number
  height?: number
  area?: number
}

export interface ProductPosition {
  id: number
  detection_id: number
  product_name: string
  brand?: string
  shelf_row?: number
  shelf_column?: number
  position_description?: string
  quantity: number
  confidence: number
  x_min?: number
  y_min?: number
  x_max?: number
  y_max?: number
  created_at: string
}

export interface QuestionRequest {
  detection_id: number
  question: string
}

export interface QuestionResponse {
  answer: string
  detection_id: number
}

export interface Statistics {
  total_detections: number
  total_objects_detected: number
  average_objects_per_detection: number
  class_distribution: Record<string, number>
  most_detected_class: string | null
}