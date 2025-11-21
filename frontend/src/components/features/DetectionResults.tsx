'use client'

import { useState } from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatConfidence } from '@/lib/utils'
import { Detection, DetectedObject } from '@/types'
import { ArrowUpDown, Image as ImageIcon } from 'lucide-react'

interface DetectionResultsProps {
  detection: Detection
}

type SortField = 'class_name' | 'confidence' | 'area'
type SortOrder = 'asc' | 'desc'

export default function DetectionResults({ detection }: DetectionResultsProps) {
  const [sortField, setSortField] = useState<SortField>('confidence')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const [selectedObject, setSelectedObject] = useState<DetectedObject | null>(null)

  const sortedObjects = [...detection.objects].sort((a, b) => {
    let aValue = a[sortField] || 0
    let bValue = b[sortField] || 0

    if (sortField === 'class_name') {
      aValue = a.class_name.toLowerCase()
      bValue = b.class_name.toLowerCase()
    }

    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1
    } else {
      return aValue < bValue ? 1 : -1
    }
  })

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  const analysisData = detection.analysis_data ? (
    typeof detection.analysis_data === 'string' 
      ? JSON.parse(detection.analysis_data)
      : detection.analysis_data
  ) : null

  return (
    <div className="space-y-6">
      {/* Images */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center">
              <ImageIcon className="h-4 w-4 mr-2" />
              Original Image
            </CardTitle>
          </CardHeader>
          <CardContent>
            <img
              src={`http://localhost:8000${detection.original_image}`}
              alt="Original"
              className="w-full h-48 object-cover rounded-lg"
            />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center">
              <ImageIcon className="h-4 w-4 mr-2" />
              Annotated Image
            </CardTitle>
          </CardHeader>
          <CardContent>
            <img
              src={`http://localhost:8000${detection.annotated_image}`}
              alt="Annotated"
              className="w-full h-48 object-cover rounded-lg"
            />
          </CardContent>
        </Card>
      </div>

      {/* Analysis Summary */}
      {analysisData && (
        <Card>
          <CardHeader>
            <CardTitle>Analysis Summary</CardTitle>
            <CardDescription>
              AI-powered insights about the detected products
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-muted-foreground">Layout Type</div>
                <div className="font-medium capitalize">
                  {analysisData.layout_type?.replace('_', ' ') || 'Unknown'}
                </div>
              </div>
              <div>
                <div className="text-muted-foreground">Estimated Rows</div>
                <div className="font-medium">
                  {analysisData.estimated_rows || 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-muted-foreground">Estimated Columns</div>
                <div className="font-medium">
                  {analysisData.estimated_columns || 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-muted-foreground">Density</div>
                <div className="font-medium">
                  {analysisData.density ? `${(analysisData.density * 100).toFixed(1)}%` : 'N/A'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Detected Objects Table */}
      <Card>
        <CardHeader>
          <CardTitle>Detected Objects</CardTitle>
          <CardDescription>
            {detection.total_objects} objects found in the image
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort('class_name')}
                    className="p-0 h-auto font-medium"
                  >
                    Class
                    <ArrowUpDown className="h-4 w-4 ml-1" />
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort('confidence')}
                    className="p-0 h-auto font-medium"
                  >
                    Confidence
                    <ArrowUpDown className="h-4 w-4 ml-1" />
                  </Button>
                </TableHead>
                <TableHead>Position</TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort('area')}
                    className="p-0 h-auto font-medium"
                  >
                    Size
                    <ArrowUpDown className="h-4 w-4 ml-1" />
                  </Button>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedObjects.map((object, index) => (
                <TableRow 
                  key={index}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => setSelectedObject(object)}
                >
                  <TableCell className="font-medium capitalize">
                    {object.class_name}
                  </TableCell>
                  <TableCell>
                    <Badge variant={object.confidence > 0.7 ? "default" : "secondary"}>
                      {formatConfidence(object.confidence)}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm">
                    ({object.x_min.toFixed(0)}, {object.y_min.toFixed(0)}) - 
                    ({object.x_max.toFixed(0)}, {object.y_max.toFixed(0)})
                  </TableCell>
                  <TableCell className="text-sm">
                    {object.area ? `${object.area.toFixed(0)} px²` : 'N/A'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}