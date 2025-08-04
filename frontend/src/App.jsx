import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { ThemeProvider } from 'next-themes';

// Layouts
import { ContentLayout, DashboardLayout, AuthLayout } from './components/layouts/PageLayout';

// Pages
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { IMCCalculatorPage } from './pages/tools/IMCCalculatorPage';
import { FoodDiaryPage } from './pages/tools/FoodDiaryPage';
import { StorePage } from './pages/store/StorePage';
import { ProductDetailPage } from './pages/store/ProductDetailPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';

// Components
import { ErrorBoundary } from './components/ui/error';

// Hooks
import { useAuth } from './lib/api';

// Theme initialization
import './lib/theme';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Carregando...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Public Route Component (redirects if already authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Carregando...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Home Page Component
const HomePage = () => {
  return (
    <ContentLayout>
      <div className="text-center py-20">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Bem-vindo ao RE-EDUCA Store
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
          Transformando vidas através da educação em saúde
        </p>
        <div className="flex justify-center space-x-4">
          <a
            href="/login"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Entrar
          </a>
          <a
            href="/register"
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Cadastrar
          </a>
        </div>
      </div>
    </ContentLayout>
  );
};

// App Component
function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <Router>
          <div className="App">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<HomePage />} />
              
              <Route 
                path="/login" 
                element={
                  <PublicRoute>
                    <LoginPage />
                  </PublicRoute>
                } 
              />
              
              <Route 
                path="/register" 
                element={
                  <PublicRoute>
                    <RegisterPage />
                  </PublicRoute>
                } 
              />

                          {/* Protected Routes */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              } 
            />

            {/* Health Tools Routes */}
            <Route 
              path="/tools/imc" 
              element={
                <ProtectedRoute>
                  <IMCCalculatorPage />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/tools/food-diary" 
              element={
                <ProtectedRoute>
                  <FoodDiaryPage />
                </ProtectedRoute>
              } 
            />

            {/* Store Routes */}
            <Route 
              path="/store" 
              element={
                <ProtectedRoute>
                  <StorePage />
                </ProtectedRoute>
              } 
            />

            <Route 
              path="/store/product/:productId" 
              element={
                <ProtectedRoute>
                  <ProductDetailPage />
                </ProtectedRoute>
              } 
            />

            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>

            {/* Toast Notifications */}
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'var(--background)',
                  color: 'var(--foreground)',
                  border: '1px solid var(--border)',
                },
              }}
            />
          </div>
        </Router>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;

