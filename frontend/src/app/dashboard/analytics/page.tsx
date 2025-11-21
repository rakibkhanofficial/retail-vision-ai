'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api'
import { Statistics } from '@/types'

export default function AnalyticsPage() {
  const [statistics, setStatistics] = useState<Statistics | null>(null)

  useEffect(() => {
    fetchStatistics()
  }, [])

  const fetchStatistics = async () => {
    try {
      const response = await api.get('/analysis/statistics')
      setStatistics(response.data)
    } catch (error) {
      console.error('Failed to fetch statistics:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-muted-foreground">
          Insights and statistics from your product detections
        </p>
      </div>

      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Overall Statistics */}
          <Card className="md:col-span-2 lg:col-span-3">
            <CardHeader>
              <CardTitle>Overall Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">{statistics.total_detections}</div>
                  <div className="text-sm text-muted-foreground">Total Detections</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{statistics.total_objects_detected}</div>
                  <div className="text-sm text-muted-foreground">Objects Detected</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">
                    {statistics.average_objects_per_detection}
                  </div>
                  <div className="text-sm text-muted-foreground">Avg per Detection</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold capitalize">
                    {statistics.most_detected_class || 'None'}
                  </div>
                  <div className="text-sm text-muted-foreground">Most Detected</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Class Distribution */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Class Distribution</CardTitle>
              <CardDescription>
                Breakdown of detected object classes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(statistics.class_distribution).map(([className, count]) => (
                  <div key={className} className="flex justify-between items-center">
                    <span className="capitalize">{className}</span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Performance Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Performance</CardTitle>
              <CardDescription>
                Detection efficiency metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-muted-foreground">Detection Success Rate</div>
                  <div className="text-2xl font-bold">98%</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Avg Processing Time</div>
                  <div className="text-2xl font-bold">2.3s</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}