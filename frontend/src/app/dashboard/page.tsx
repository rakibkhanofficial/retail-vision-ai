'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useDetection } from '@/hooks/useDetection'
import ImageUploader from '@/components/features/ImageUploader'
import DetectionResults from '@/components/features/DetectionResults'
import api from '@/lib/api'
import { useSession } from 'next-auth/react'
import { Statistics } from '@/types'

export default function DashboardPage() {
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const { currentDetection, isLoading } = useDetection()
  const { data: session } = useSession()

  useEffect(() => {
    if (session?.accessToken) {
      fetchStatistics()
    }
  }, [session])

  const fetchStatistics = async () => {
    if (!session?.accessToken) return
    
    try {
      const response = await api.get('/analysis/statistics')
      setStatistics(response.data)
    } catch (error) {
      console.error('Failed to fetch statistics:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Analyze retail products with AI-powered detection
          </p>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Detections</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_detections}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Objects Detected</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_objects_detected}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Avg Objects/Detection</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics.average_objects_per_detection}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Most Detected</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics.most_detected_class || 'None'}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Image</CardTitle>
          <CardDescription>
            Upload an image of retail products for AI analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ImageUploader onUploadComplete={fetchStatistics} />
        </CardContent>
      </Card>

      {/* Recent Detection Results */}
      {currentDetection && (
        <Card>
          <CardHeader>
            <CardTitle>Latest Detection Results</CardTitle>
            <CardDescription>
              Analysis of your most recent image upload
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DetectionResults detection={currentDetection} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}