import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

export default function CTA() {
  return (
    <section className="py-24 bg-slate-900 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -right-1/2 w-[1000px] h-[1000px] bg-blue-600/20 rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -left-1/2 w-[1000px] h-[1000px] bg-indigo-600/20 rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 relative z-10 text-center">
        <div className="max-w-3xl mx-auto space-y-8">
          <h2 className="text-3xl md:text-5xl font-bold text-white tracking-tight">
            Ready to revolutionize your retail analytics?
          </h2>
          <p className="text-xl text-slate-300 leading-relaxed">
            Join forward-thinking retailers using AI to optimize product placements, reduce out-of-stocks, and drive revenue growth.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
            <Link href="/register">
              <Button size="lg" className="h-14 px-8 text-lg bg-white text-slate-900 hover:bg-slate-100">
                Start Your Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/contact">
              <Button size="lg" variant="outline" className="h-14 px-8 text-lg border-slate-700 text-white hover:bg-slate-800 hover:text-white">
                Contact Sales
              </Button>
            </Link>
          </div>
          <p className="text-sm text-slate-500 pt-4">
            No credit card required · 14-day free trial · Cancel anytime
          </p>
        </div>
      </div>
    </section>
  )
}