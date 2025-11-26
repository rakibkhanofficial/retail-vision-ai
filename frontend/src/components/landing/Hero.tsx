import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { ArrowRight, CheckCircle2 } from 'lucide-react'

export default function Hero() {
  return (
    <section className="relative pt-32 pb-20 lg:pt-40 lg:pb-28 overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full z-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-100 rounded-full blur-3xl opacity-50 mix-blend-multiply animate-blob" />
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-indigo-100 rounded-full blur-3xl opacity-50 mix-blend-multiply animate-blob animation-delay-2000" />
        <div className="absolute -bottom-32 left-1/3 w-[500px] h-[500px] bg-purple-100 rounded-full blur-3xl opacity-50 mix-blend-multiply animate-blob animation-delay-4000" />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="flex flex-col lg:flex-row items-center gap-12 lg:gap-20">

          {/* Text Content */}
          <div className="lg:w-1/2 space-y-8 text-center lg:text-left">
            <div className="space-y-4">
              <div className="inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium bg-white/50 backdrop-blur-sm">
                <span className="flex h-2 w-2 rounded-full bg-blue-600 mr-2"></span>
                New: Advanced Shelf Analytics 2.0
              </div>
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-slate-900 leading-[1.1]">
                Retail Intelligence{' '}
                <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Reimagined
                </span>
              </h1>
              <p className="text-xl text-slate-600 max-w-2xl mx-auto lg:mx-0 leading-relaxed">
                Transform your retail operations with AI-powered product detection.
                Get real-time insights, optimize shelf space, and boost sales with 99.9% accuracy.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link href="/register">
                <Button size="lg" className="h-12 px-8 text-base bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/25">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/demo">
                <Button size="lg" variant="outline" className="h-12 px-8 text-base">
                  View Demo
                </Button>
              </Link>
            </div>

            <div className="pt-4 flex items-center justify-center lg:justify-start gap-6 text-sm text-slate-500">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>14-day free trial</span>
              </div>
            </div>
          </div>

          {/* Visual Content */}
          <div className="lg:w-1/2 relative">
            <div className="relative rounded-2xl border bg-white/50 backdrop-blur-sm p-2 shadow-2xl">
              <div className="rounded-xl overflow-hidden bg-slate-100 aspect-[4/3] relative group">
                {/* Abstract UI representation */}
                <div className="absolute inset-0 bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center">
                  <div className="w-3/4 h-3/4 bg-white rounded-lg shadow-sm p-4 space-y-3">
                    <div className="flex gap-2">
                      <div className="w-2/3 h-24 bg-blue-50 rounded-md animate-pulse" />
                      <div className="w-1/3 h-24 bg-indigo-50 rounded-md animate-pulse" />
                    </div>
                    <div className="h-4 bg-slate-100 rounded w-3/4" />
                    <div className="h-4 bg-slate-100 rounded w-1/2" />
                    <div className="grid grid-cols-3 gap-2 pt-2">
                      <div className="h-16 bg-slate-50 rounded" />
                      <div className="h-16 bg-slate-50 rounded" />
                      <div className="h-16 bg-slate-50 rounded" />
                    </div>
                  </div>
                </div>

                {/* Overlay Badge */}
                <div className="absolute bottom-6 left-6 bg-white/90 backdrop-blur rounded-lg p-3 shadow-lg border border-slate-100 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                    <CheckCircle2 className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground font-medium">Detection Accuracy</p>
                    <p className="text-lg font-bold text-slate-900">99.9%</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}