'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/lib/api'
import { Detection } from '@/types'
import DetectionResults from '@/components/features/DetectionResults'
import ProductAnalysis from '@/components/features/ProductAnalysis'
import ChatInterface from '@/components/features/ChatInterface'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function DetectionDetailPage() {
  const params = useParams()
  const [detection, setDetection] = useState<Detection | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (params.id) {
      fetchDetection()
    }
  }, [params.id])

  const fetchDetection = async () => {
    try {
      const response = await api.get(`/detections/${params.id}`)
      setDetection(response.data)
    } catch (error) {
      console.error('Failed to fetch detection:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading detection...</div>
  }

  if (!detection) {
    return (
      <div className="text-center py-8">
        <h2 className="text-2xl font-bold mb-4">Detection not found</h2>
        <Link href="/detections">
          <Button>Back to Detections</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/detections">
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">{detection.name}</h1>
          <p className="text-muted-foreground">
            Detailed analysis of product detection
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Detection Results */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Detection Results</CardTitle>
            <CardDescription>
              Object detection and analysis results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DetectionResults detection={detection} />
          </CardContent>
        </Card>

        {/* Product Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>Product Analysis</CardTitle>
            <CardDescription>
              AI-powered retail product insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ProductAnalysis detection={detection} />
          </CardContent>
        </Card>

        {/* Chat Interface */}
        <Card>
          <CardHeader>
            <CardTitle>AI Assistant</CardTitle>
            <CardDescription>
              Ask questions about this detection
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ChatInterface detection={detection} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}