import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PaperPlaneRight, Warning, CheckCircle } from '@phosphor-icons/react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import axios from 'axios';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ChatInterface = ({ token, conversationId, onConversationCreated }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (conversationId) {
      loadConversationHistory();
    } else {
      setMessages([]);
    }
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const loadConversationHistory = async () => {
    setLoadingHistory(true);
    try {
      const response = await axios.get(
        `${API}/conversations/${conversationId}/messages`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessages(response.data);
    } catch (error) {
      console.error('Error loading conversation:', error);
      toast.error('Failed to load conversation');
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message to UI
    const tempUserMsg = {
      id: 'temp-user',
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const response = await axios.post(
        `${API}/chat`,
        {
          message: userMessage,
          conversation_id: conversationId
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Add Athena's response
      const athenaMsg = {
        id: response.data.message_id,
        role: 'assistant',
        content: response.data.response,
        bias_analysis: response.data.bias_analysis,
        timestamp: new Date().toISOString()
      };

      setMessages((prev) => [
        ...prev.filter((m) => m.id !== 'temp-user'),
        { ...tempUserMsg, id: 'user-' + Date.now() },
        athenaMsg
      ]);

      // If new conversation, notify parent
      if (!conversationId && response.data.conversation_id) {
        onConversationCreated(response.data.conversation_id);
      }
    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to send message');
      setMessages((prev) => prev.filter((m) => m.id !== 'temp-user'));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Welcome / Chat Area */}
      <div className="flex-1 overflow-hidden">
        {messages.length === 0 && !loadingHistory ? (
          // Welcome Screen
          <div className="h-full flex items-center justify-center p-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-center max-w-2xl"
            >
              <img
                src="athena.png"
                alt="Athena"
                className="w-32 h-32 mx-auto mb-6 object-contain"
                style={{ filter: 'drop-shadow(0 0 25px rgba(212, 175, 55, 0.5))' }}
              />
              <h2
                className="text-4xl font-medium mb-4"
                style={{
                  fontFamily: "'Cormorant Garamond', serif",
                  color: '#D4AF37'
                }}
              >
                I am Athena
              </h2>
              <p className="text-base leading-relaxed mb-6" style={{ color: '#94A3B8' }}>
                I'm your thoughtful AI companion for unbiased reasoning and fair analysis.
                I help you make wise decisions based on merit, not demographics. Let's explore questions together!
              </p>
              <p
                className="text-sm uppercase tracking-[0.2em]"
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  color: '#475569'
                }}
              >
                Ask me anything
              </p>
            </motion.div>
          </div>
        ) : (
          // Messages
          <ScrollArea className="h-full">
            <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
              {loadingHistory ? (
                <div className="text-center py-12">
                  <div
                    className="w-8 h-8 border-2 border-t-transparent rounded-full mx-auto animate-spin"
                    style={{ borderColor: '#D4AF37', borderTopColor: 'transparent' }}
                  />
                </div>
              ) : (
                <AnimatePresence>
                  {messages.map((msg, idx) => (
                    <motion.div
                      key={msg.id || idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                      data-testid={`message-${msg.role}`}
                    >
                      {msg.role === 'user' ? (
                        // User Message
                        <div className="flex justify-end">
                          <div
                            className="max-w-[80%] p-4 rounded-md"
                            style={{
                              backgroundColor: 'rgba(255, 255, 255, 0.03)',
                              borderLeft: '3px solid rgba(255, 255, 255, 0.1)'
                            }}
                          >
                            <p className="text-base" style={{ color: '#F8FAFC' }}>
                              {msg.content}
                            </p>
                          </div>
                        </div>
                      ) : (
                        // Athena Message
                        <div className="flex gap-4">
                          <img
                            src="athena.png"
                            alt="Athena"
                            className="w-12 h-12 flex-shrink-0 object-contain"
                            style={{ filter: 'drop-shadow(0 0 15px rgba(212, 175, 55, 0.4))' }}
                          />
                          <div className="flex-1">
                            <div
                              className="p-4 rounded-md border"
                              style={{
                                backgroundColor: '#0B101A',
                                borderColor: '#D4AF37'
                              }}
                            >
                              <p
                                className="text-base leading-relaxed whitespace-pre-wrap"
                                style={{
                                  fontFamily: "'Cormorant Garamond', serif",
                                  color: '#F8FAFC'
                                }}
                              >
                                {msg.content}
                              </p>
                            </div>

                            {/* Bias Analysis Badge */}
                            {msg.bias_analysis && msg.bias_analysis !== 'neutral' && (
                              <div className="mt-2 flex items-center gap-2">
                                {msg.bias_analysis === 'bias_aware' ? (
                                  <>
                                    <Warning size={16} weight="duotone" style={{ color: '#EF4444' }} />
                                    <span
                                      className="text-xs uppercase tracking-[0.2em]"
                                      style={{
                                        fontFamily: "'IBM Plex Mono', monospace",
                                        color: '#EF4444'
                                      }}
                                    >
                                      Bias-Aware Response
                                    </span>
                                  </>
                                ) : (
                                  <>
                                    <CheckCircle size={16} weight="duotone" style={{ color: '#10B981' }} />
                                    <span
                                      className="text-xs uppercase tracking-[0.2em]"
                                      style={{
                                        fontFamily: "'IBM Plex Mono', monospace",
                                        color: '#10B981'
                                      }}
                                    >
                                      Unbiased Analysis
                                    </span>
                                  </>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
              )}
              <div ref={scrollRef} />
            </div>
          </ScrollArea>
        )}
      </div>

      {/* Input Area */}
      <div
        className="border-t p-6"
        style={{
          backgroundColor: '#0B101A',
          borderColor: 'rgba(255, 255, 255, 0.1)'
        }}
      >
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <Textarea
              data-testid="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask Athena for unbiased reasoning..."
              disabled={loading}
              rows={3}
              className="flex-1 resize-none bg-transparent border rounded-md focus:border-[#D4AF37] transition-colors duration-300"
              style={{
                borderColor: 'rgba(255, 255, 255, 0.1)',
                color: '#F8FAFC'
              }}
            />
            <Button
              data-testid="chat-send-button"
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="h-full px-6 transition-all duration-300"
              style={{
                backgroundColor: loading || !input.trim() ? '#475569' : '#D4AF37',
                color: '#030712'
              }}
              onMouseEnter={(e) => {
                if (!loading && input.trim()) {
                  e.target.style.backgroundColor = '#FBE689';
                }
              }}
              onMouseLeave={(e) => {
                if (!loading && input.trim()) {
                  e.target.style.backgroundColor = '#D4AF37';
                }
              }}
            >
              {loading ? (
                <div
                  className="w-5 h-5 border-2 border-t-transparent rounded-full animate-spin"
                  style={{ borderColor: '#030712', borderTopColor: 'transparent' }}
                />
              ) : (
                <PaperPlaneRight size={20} weight="bold" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
