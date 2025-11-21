'use client'

import { Detection } from '@/types'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Package, Star, MapPin, BarChart3 } from 'lucide-react'

interface ProductAnalysisProps {
  detection: Detection
}

export default function ProductAnalysis({ detection }: ProductAnalysisProps) {
  const analysisData = detection.analysis_data ? (
    typeof detection.analysis_data === 'string' 
      ? JSON.parse(detection.analysis_data)
      : detection.analysis_data
  ) : null

  const retailAnalysis = analysisData?.retail_analysis

  if (!retailAnalysis) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Product Analysis</CardTitle>
          <CardDescription>
            AI-powered retail insights will appear here
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <Package className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No retail analysis available</p>
            <p className="text-sm">Make sure GEMINI_API_KEY is configured</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Brands Detected */}
      {retailAnalysis.brands_detected?.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center">
              <Star className="h-4 w-4 mr-2" />
              Brands Detected
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {retailAnalysis.brands_detected.map((brand: string, index: number) => (
                <Badge key={index} variant="secondary">
                  {brand}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Product Categories */}
      {retailAnalysis.product_categories?.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center">
              <Package className="h-4 w-4 mr-2" />
              Product Categories
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {retailAnalysis.product_categories.map((category: string, index: number) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm">{category}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Shelf Organization */}
      {retailAnalysis.shelf_organization && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center">
              <MapPin className="h-4 w-4 mr-2" />
              Shelf Organization
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{retailAnalysis.shelf_organization}</p>
          </CardContent>
        </Card>
      )}

      {/* Stock Levels */}
      {retailAnalysis.stock_levels && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center">
              <BarChart3 className="h-4 w-4 mr-2" />
              Stock Levels
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{retailAnalysis.stock_levels}</p>
          </CardContent>
        </Card>
      )}

      {/* Product Positions */}
      {detection.products.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Product Positions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {detection.products.map((product) => (
                <div key={product.id} className="flex justify-between items-center p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">{product.product_name}</div>
                    {product.brand && (
                      <div className="text-sm text-muted-foreground">{product.brand}</div>
                    )}
                    {(product.shelf_row !== null && product.shelf_column !== null) && (
                      <div className="text-xs text-muted-foreground">
                        Row {product.shelf_row}, Col {product.shelf_column}
                      </div>
                    )}
                  </div>
                  <Badge variant="outline">
                    {product.quantity} unit{product.quantity > 1 ? 's' : ''}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}