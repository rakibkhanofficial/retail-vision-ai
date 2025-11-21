'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { formatDate } from '@/lib/utils'
import { useSession } from 'next-auth/react'
import { Detection } from '@/types'
import Link from 'next/link'
import { Eye, Trash2 } from 'lucide-react'
import api from '@/lib/api'

export default function DetectionsPage() {
  const [detections, setDetections] = useState<Detection[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { data: session } = useSession()

  useEffect(() => {
    if (session?.accessToken) {
      fetchDetections()
    }
  }, [session])

  const fetchDetections = async () => {
    if (!session?.accessToken) return
    
    try {
      const response = await api.get('/detections?limit=50')
      setDetections(response.data)
    } catch (error) {
      console.error('Failed to fetch detections:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const deleteDetection = async (id: number) => {
    if (!session?.accessToken || !confirm('Are you sure you want to delete this detection?')) return

    try {
      await api.delete(`/detections/${id}`)
      setDetections(detections.filter(d => d.id !== id))
    } catch (error) {
      console.error('Failed to delete detection:', error)
    }
  }

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading detections...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Detections</h1>
          <p className="text-muted-foreground">
            View and manage your product detection history
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Detection History</CardTitle>
          <CardDescription>
            All your product detection analyses in one place
          </CardDescription>
        </CardHeader>
        <CardContent>
          {detections.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No detections found. Upload an image to get started.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Objects</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {detections.map((detection) => (
                  <TableRow key={detection.id}>
                    <TableCell className="font-medium">
                      {detection.name}
                    </TableCell>
                    <TableCell>{detection.total_objects}</TableCell>
                    <TableCell>{formatDate(detection.created_at)}</TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Link href={`/detections/${detection.id}`}>
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                        </Link>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => deleteDetection(detection.id)}
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Delete
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}