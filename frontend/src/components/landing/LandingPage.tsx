import Hero from './Hero'
import Features from './Features'
import CTA from './CTA'

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <Hero />
      <Features />
      <CTA />
    </div>
  )
}