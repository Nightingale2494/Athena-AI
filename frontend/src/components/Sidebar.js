import { motion, AnimatePresence } from 'framer-motion';
import { X, Plus, ChatCircle, FileText } from '@phosphor-icons/react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';

const Sidebar = ({
  open,
  conversations,
  currentConversationId,
  onNewConversation,
  onSelectConversation,
  onShowUpload,
  onClose
}) => {
  return (
    <>
      {/* Mobile Overlay */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ x: open ? 0 : -320 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="fixed lg:sticky top-0 left-0 h-screen z-50 border-r"
        style={{
          width: '320px',
          backgroundColor: '#0B101A',
          borderColor: 'rgba(255, 255, 255, 0.1)'
        }}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b" style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}>
            <div className="flex items-center justify-between mb-4">
              <h2
                className="text-xl font-normal"
                style={{
                  fontFamily: "'Cormorant Garamond', serif",
                  color: '#F8FAFC'
                }}
              >
                Conversations
              </h2>
              <button
                onClick={onClose}
                className="lg:hidden p-1"
                style={{ color: '#94A3B8' }}
              >
                <X size={20} />
              </button>
            </div>

            <Button
              data-testid="new-conversation-button"
              onClick={onNewConversation}
              className="w-full gap-2 text-sm font-medium tracking-wide transition-all duration-300"
              style={{
                backgroundColor: '#D4AF37',
                color: '#030712'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#FBE689';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = '#D4AF37';
              }}
            >
              <Plus size={18} weight="bold" />
              New Chat
            </Button>
          </div>

          {/* Upload Button */}
          <div className="px-6 py-4 border-b" style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}>
            <button
              data-testid="upload-document-button"
              onClick={onShowUpload}
              className="w-full flex items-center gap-3 p-3 rounded-md transition-all duration-300"
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.03)',
                color: '#94A3B8'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.06)';
                e.target.style.color = '#D4AF37';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.03)';
                e.target.style.color = '#94A3B8';
              }}
            >
              <FileText size={20} weight="duotone" />
              <span className="text-sm">Analyze Document</span>
            </button>
          </div>

          {/* Conversations List */}
          <ScrollArea className="flex-1 px-6 py-4">
            <div className="space-y-2">
              {conversations.length === 0 ? (
                <p className="text-sm text-center py-8" style={{ color: '#475569' }}>
                  No conversations yet
                </p>
              ) : (
                conversations.map((conv) => (
                  <button
                    key={conv.id}
                    data-testid={`conversation-${conv.id}`}
                    onClick={() => onSelectConversation(conv.id)}
                    className="w-full text-left p-3 rounded-md transition-all duration-300"
                    style={{
                      backgroundColor:
                        currentConversationId === conv.id
                          ? 'rgba(212, 175, 55, 0.1)'
                          : 'rgba(255, 255, 255, 0.03)',
                      borderLeft:
                        currentConversationId === conv.id
                          ? '3px solid #D4AF37'
                          : '3px solid transparent',
                      color: currentConversationId === conv.id ? '#D4AF37' : '#94A3B8'
                    }}
                    onMouseEnter={(e) => {
                      if (currentConversationId !== conv.id) {
                        e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.06)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (currentConversationId !== conv.id) {
                        e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.03)';
                      }
                    }}
                  >
                    <div className="flex items-start gap-2">
                      <ChatCircle size={18} weight="duotone" className="mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{conv.title}</p>
                        <p
                          className="text-xs mt-1"
                          style={{
                            fontFamily: "'IBM Plex Mono', monospace",
                            color: '#475569'
                          }}
                        >
                          {conv.message_count} messages
                        </p>
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>
          </ScrollArea>
        </div>
      </motion.aside>
    </>
  );
};

export default Sidebar;
