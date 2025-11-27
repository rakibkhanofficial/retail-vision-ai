'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Scan, Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function Navbar() {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

    return (
        <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <Link href="/" className="flex items-center space-x-2">
                    <div className="bg-gradient-to-tr from-blue-600 to-indigo-600 p-2 rounded-lg">
                        <Scan className="h-6 w-6 text-white" />
                    </div>
                    <span className="font-bold text-xl tracking-tight">Retail Vision AI</span>
                </Link>

                {/* Desktop Navigation */}
                <div className="hidden md:flex items-center space-x-8">
                    <Link href="#features" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                        Features
                    </Link>
                    <Link href="#how-it-works" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                        How it Works
                    </Link>
                    <Link href="#pricing" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
                        Pricing
                    </Link>
                </div>

                <div className="hidden md:flex items-center space-x-4">
                    <Link href="/login">
                        <Button variant="ghost" className="font-medium">
                            Sign In
                        </Button>
                    </Link>
                    <Link href="/register">
                        <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg shadow-blue-500/25">
                            Get Started
                        </Button>
                    </Link>
                </div>

                {/* Mobile Navigation */}
                <div className="md:hidden">
                    <Button variant="ghost" size="icon" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
                        <Menu className="h-6 w-6" />
                    </Button>
                </div>
            </div>

            {/* Mobile Menu Overlay */}
            {isMobileMenuOpen && (
                <div className="md:hidden absolute top-16 left-0 w-full bg-white border-b border-gray-100 p-4 shadow-lg animate-in slide-in-from-top-5">
                    <div className="flex flex-col space-y-4">
                        <Link
                            href="#features"
                            className="text-lg font-medium p-2 hover:bg-slate-50 rounded-md"
                            onClick={() => setIsMobileMenuOpen(false)}
                        >
                            Features
                        </Link>
                        <Link
                            href="#how-it-works"
                            className="text-lg font-medium p-2 hover:bg-slate-50 rounded-md"
                            onClick={() => setIsMobileMenuOpen(false)}
                        >
                            How it Works
                        </Link>
                        <Link
                            href="#pricing"
                            className="text-lg font-medium p-2 hover:bg-slate-50 rounded-md"
                            onClick={() => setIsMobileMenuOpen(false)}
                        >
                            Pricing
                        </Link>
                        <hr className="my-2" />
                        <Link href="/login" onClick={() => setIsMobileMenuOpen(false)}>
                            <Button variant="ghost" className="w-full justify-start">
                                Sign In
                            </Button>
                        </Link>
                        <Link href="/register" onClick={() => setIsMobileMenuOpen(false)}>
                            <Button className="w-full bg-gradient-to-r from-blue-600 to-indigo-600">
                                Get Started
                            </Button>
                        </Link>
                    </div>
                </div>
            )}
        </nav>
    )
}
