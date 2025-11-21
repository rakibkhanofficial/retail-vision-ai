'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useDetection } from '@/hooks/useDetection'
import { useSession } from 'next-auth/react'
import { Upload, Camera, X } from 'lucide-react'
import CameraCapture from './CameraCapture'
import api from '@/lib/api'

interface ImageUploaderProps {
  onUploadComplete?: () => void
}

export default function ImageUploader({ onUploadComplete }: ImageUploaderProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [showCamera, setShowCamera] = useState(false)
  const { setCurrentDetection } = useDetection()
  const { data: session } = useSession()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0 || !session?.accessToken) return

    const file = acceptedFiles[0]
    await uploadImage(file)
  }, [session])

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: false,
    disabled: isUploading || !session?.accessToken
  })

  const uploadImage = async (file: File) => {
    if (!session?.accessToken) return
    
    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', `Detection ${new Date().toLocaleString()}`)

    try {
      const response = await api.post('/detections', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setCurrentDetection(response.data)
      onUploadComplete?.()
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleCameraCapture = async (imageBlob: Blob) => {
    if (!session?.accessToken) return
    
    const file = new File([imageBlob], `camera-capture-${Date.now()}.jpg`, {
      type: 'image/jpeg'
    })
    await uploadImage(file)
    setShowCamera(false)
  }

  if (showCamera) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Capture from Camera</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowCamera(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <CameraCapture onCapture={handleCameraCapture} />
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex space-x-4">
        <Button
          onClick={open}
          disabled={isUploading || !session?.accessToken}
          className="flex-1"
        >
          <Upload className="h-4 w-4 mr-2" />
          Upload Image
        </Button>
        <Button
          variant="outline"
          onClick={() => setShowCamera(true)}
          disabled={isUploading || !session?.accessToken}
          className="flex-1"
        >
          <Camera className="h-4 w-4 mr-2" />
          Use Camera
        </Button>
      </div>

      <Card>
        <CardContent className="p-6">
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'}
              ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
              ${!session?.accessToken ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            {isUploading ? (
              <div className="space-y-2">
                <p className="font-medium">Uploading image...</p>
                <p className="text-sm text-muted-foreground">
                  Processing your image with AI
                </p>
              </div>
            ) : isDragActive ? (
              <div className="space-y-2">
                <p className="font-medium">Drop the image here</p>
                <p className="text-sm text-muted-foreground">
                  Release to upload and analyze
                </p>
              </div>
            ) : !session?.accessToken ? (
              <div className="space-y-2">
                <p className="font-medium">Please sign in to upload images</p>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="font-medium">Drag & drop an image here</p>
                <p className="text-sm text-muted-foreground">
                  or click to select a file
                </p>
                <p className="text-xs text-muted-foreground">
                  Supports JPG, PNG, WebP • Max 10MB
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}