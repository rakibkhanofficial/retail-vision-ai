import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Camera, Scan, BarChart3, MessageSquare } from 'lucide-react'

const features = [
  {
    icon: Camera,
    title: 'Multiple Upload Options',
    description: 'Upload images via file upload, drag & drop, or direct camera capture'
  },
  {
    icon: Scan,
    title: 'AI-Powered Detection',
    description: 'Advanced YOLO object detection with retail-specific product recognition'
  },
  {
    icon: BarChart3,
    title: 'Product Analytics',
    description: 'Get detailed insights about brands, positioning, and stock levels'
  },
  {
    icon: MessageSquare,
    title: 'AI Assistant',
    description: 'Ask questions about your detections and get intelligent responses'
  }
]

export default function Features() {
  return (
    <section className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center space-y-4 mb-12">
          <h2 className="text-3xl md:text-4xl font-bold">Powerful Features</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need to analyze retail product placements and optimize your shelves
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="text-center">
              <CardHeader>
                <div className="flex justify-center mb-4">
                  <div className="p-3 bg-primary/10 rounded-lg">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                </div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{feature.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}