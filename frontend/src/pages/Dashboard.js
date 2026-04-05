import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { signOut } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import ChatInterface from '@/components/ChatInterface';
import DocumentUpload from '@/components/DocumentUpload';
import Sidebar from '@/components/Sidebar';
import { Button } from '@/components/ui/button';
import { SignOut, List } from '@phosphor-icons/react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Dashboard = () => {
  const { user, token, loading } = useAuth();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      navigate('/auth');
    }
  }, [user, loading, navigate]);

  useEffect(() => {
    if (token) {
      loadConversations();
    }
  }, [token]);

  const loadConversations = async () => {
    try {
      const response = await axios.get(`${API}/conversations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConversations(response.data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
      toast.success('Logged out successfully');
      navigate('/auth');
    } catch (error) {
      toast.error('Error logging out');
    }
  };

  const handleNewConversation = () => {
    setCurrentConversationId(null);
    setShowUpload(false);
  };

  const handleSelectConversation = (id) => {
    setCurrentConversationId(id);
    setShowUpload(false);
  };

  const handleShowUpload = () => {
    setShowUpload(true);
    setCurrentConversationId(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#030712' }}>
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-12 h-12 border-2 border-t-transparent rounded-full mx-auto mb-4"
            style={{ borderColor: '#D4AF37', borderTopColor: 'transparent' }}
          />
          <p style={{ color: '#94A3B8' }}>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex" style={{ backgroundColor: '#030712', fontFamily: "'IBM Plex Sans', sans-serif" }}>
      {/* Sidebar */}
      <Sidebar
        open={sidebarOpen}
        conversations={conversations}
        currentConversationId={currentConversationId}
        onNewConversation={handleNewConversation}
        onSelectConversation={handleSelectConversation}
        onShowUpload={handleShowUpload}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header
          className="sticky top-0 z-50 backdrop-blur-xl border-b"
          style={{
            backgroundColor: 'rgba(3, 7, 18, 0.8)',
            borderColor: 'rgba(255, 255, 255, 0.1)'
          }}
        >
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                data-testid="sidebar-toggle-button"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-md transition-colors duration-300"
                style={{ color: '#D4AF37' }}
              >
                <List size={24} weight="duotone" />
              </button>
              <h1
                className="text-2xl font-medium"
                style={{
                  fontFamily: "'Cormorant Garamond', serif",
                  color: '#D4AF37',
                  letterSpacing: '0.02em'
                }}
              >
                ATHENA
              </h1>
            </div>

            <div className="flex items-center gap-4">
              <span className="text-sm" style={{ color: '#94A3B8' }}>
                {user?.email}
              </span>
              <Button
                data-testid="logout-button"
                onClick={handleLogout}
                variant="ghost"
                size="sm"
                className="gap-2"
                style={{ color: '#94A3B8' }}
              >
                <SignOut size={18} />
                Sign Out
              </Button>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden">
          {showUpload ? (
            <DocumentUpload token={token} />
          ) : (
            <ChatInterface
              token={token}
              conversationId={currentConversationId}
              onConversationCreated={(id) => {
                setCurrentConversationId(id);
                loadConversations();
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
