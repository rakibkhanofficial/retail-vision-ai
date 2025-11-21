import { create } from 'zustand'
import { Detection } from '@/types'

interface DetectionState {
  currentDetection: Detection | null
  setCurrentDetection: (detection: Detection | null) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export const useDetection = create<DetectionState>((set) => ({
  currentDetection: null,
  setCurrentDetection: (detection) => set({ currentDetection: detection }),
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),
}))