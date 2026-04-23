import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  isAuthenticated: boolean
  user: {
    username: string
    email?: string
  } | null
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      login: async (username: string, password: string) => {
        // Mock authentication - 实际项目中应该调用后端API
        if (username && password) {
          set({
            isAuthenticated: true,
            user: { username, email: `${username}@example.com` },
          })
          return true
        }
        return false
      },
      logout: () => {
        set({ isAuthenticated: false, user: null })
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)

// Made with Bob
