// lib/api.ts or wherever you keep it
import axios from 'axios'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { getSession } from 'next-auth/react'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Universal interceptor that works on BOTH server & client
api.interceptors.request.use(async (config) => {
  let accessToken: string | null = null

  // 1. Server-side (API routes, server components, route handlers)
  if (typeof window === 'undefined') {
    const session = await getServerSession(authOptions)
    accessToken = session?.accessToken ?? null
  } 
  // 2. Client-side (useSession, components, hooks)
  else {
    const session = await getSession()
    accessToken = session?.accessToken ?? null
  }

  // Inject token if exists
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }

  return config
})

// Global error handler (401 → redirect to login)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      // Clear any stale session and redirect
      window.location.href = '/login?callbackUrl=' + encodeURIComponent(window.location.pathname)
    }
    return Promise.reject(error)
  }
)

export default api