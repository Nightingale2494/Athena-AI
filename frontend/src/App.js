import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import { Toaster } from '@/components/ui/sonner';
import AuthPage from '@/pages/AuthPage';
import Dashboard from '@/pages/Dashboard';
import '@/App.css';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#0B101A',
              color: '#F8FAFC',
              border: '1px solid rgba(255, 255, 255, 0.1)'
            }
          }}
        />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
