import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { Header } from '@/components/layout/Header'
import { Landing } from '@/pages/Landing'
import { Auth } from '@/pages/Auth'
import { Pricing } from '@/pages/Pricing'
import { ResearchApp } from '@/pages/ResearchApp'
import { Toaster } from '@/components/ui/sonner'
import './App.css'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }
  
  return user ? <>{children}</> : <Navigate to="/auth" />
}

function AppRoutes() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route 
            path="/app" 
            element={
              <ProtectedRoute>
                <ResearchApp />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </main>
      <Toaster />
    </div>
  )
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <AppRoutes />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App