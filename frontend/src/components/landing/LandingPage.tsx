import Hero from './Hero'
import Features from './Features'
import CTA from './CTA'
import Navbar from './Navbar'
import Footer from './Footer'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <Hero />
        <Features />
        <CTA />
      </main>
      <Footer />
    </div>
  )
}