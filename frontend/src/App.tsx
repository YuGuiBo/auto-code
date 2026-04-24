import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import LoginPage from './pages/LoginPage'
import HomePage from './pages/HomePage'
import { ProcessDesignPage } from './pages/ProcessDesignPage'
import { RequirementsPage } from './pages/RequirementsPage'
import { UserCasesPage } from './pages/UserCasesPage'
import { BPMNPage } from './pages/BPMNPage'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <HomePage />
            </PrivateRoute>
          }
        />
        <Route
          path="/design"
          element={
            <PrivateRoute>
              <ProcessDesignPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/requirements"
          element={
            <PrivateRoute>
              <RequirementsPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/cases"
          element={
            <PrivateRoute>
              <UserCasesPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/bpmn"
          element={
            <PrivateRoute>
              <BPMNPage />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App

// Made with Bob
