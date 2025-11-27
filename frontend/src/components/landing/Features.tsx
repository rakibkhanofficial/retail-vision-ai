import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Camera, Scan, BarChart3, MessageSquare, Zap, Shield, Smartphone, Globe } from 'lucide-react'

const features = [
  {
    icon: Camera,
    title: 'Smart Capture',
    description: 'Upload images via file upload, drag & drop, or direct camera capture with instant processing.',
    color: 'text-blue-600',
    bg: 'bg-blue-50'
  },
  {
    icon: Scan,
    title: 'Precision Detection',
    description: 'Advanced YOLO object detection identifies products with 99.9% accuracy in varying lighting.',
    color: 'text-indigo-600',
    bg: 'bg-indigo-50'
  },
  {
    icon: BarChart3,
    title: 'Deep Analytics',
    description: 'Get detailed insights about brand positioning, share of shelf, and stock level alerts.',
    color: 'text-purple-600',
    bg: 'bg-purple-50'
  },
  {
    icon: MessageSquare,
    title: 'AI Assistant',
    description: 'Chat with your data. Ask questions about your inventory and get intelligent, actionable responses.',
    color: 'text-pink-600',
    bg: 'bg-pink-50'
  },
  {
    icon: Zap,
    title: 'Real-time Processing',
    description: 'Process thousands of images in seconds with our distributed cloud architecture.',
    color: 'text-amber-600',
    bg: 'bg-amber-50'
  },
  {
    icon: Shield,
    title: 'Enterprise Security',
    description: 'Bank-grade encryption and SOC2 compliant infrastructure to keep your data safe.',
    color: 'text-emerald-600',
    bg: 'bg-emerald-50'
  }
]

export default function Features() {
  return (
    <section id="features" className="py-24 bg-slate-50">
      <div className="container mx-auto px-4">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900">
            Everything you need to master your shelf
          </h2>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Powerful tools designed to help you analyze retail product placements and optimize your inventory strategy.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card key={index} className="border-none shadow-lg shadow-slate-200/50 hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
              <CardHeader>
                <div className={`w-12 h-12 rounded-lg ${feature.bg} flex items-center justify-center mb-4`}>
                  <feature.icon className={`h-6 w-6 ${feature.color}`} />
                </div>
                <CardTitle className="text-xl font-bold">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-600 leading-relaxed">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}