import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { UploadSimple, FileText, CheckCircle, PaperPlaneRight } from '@phosphor-icons/react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Textarea } from '@/components/ui/textarea';
import axios from 'axios';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const DocumentUpload = ({ token }) => {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [documentText, setDocumentText] = useState('');
  const [docChatMessages, setDocChatMessages] = useState([]);
  const [docChatInput, setDocChatInput] = useState('');
  const [docChatLoading, setDocChatLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setAnalysis(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/upload`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      setAnalysis(response.data);
      setDocumentText(response.data.document_text || '');
      setDocChatMessages([]);
      setDocChatInput('');
      toast.success('Document analyzed successfully!');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(
        error.response?.data?.detail ||
        error.response?.data?.error ||
        'Failed to analyze document'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setAnalysis(null);
    setDocumentText('');
    setDocChatMessages([]);
    setDocChatInput('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDocChatSend = async () => {
    if (!docChatInput.trim() || docChatLoading) return;

    const userMessage = docChatInput.trim();
    setDocChatInput('');
    const nextMessages = [...docChatMessages, { role: 'user', content: userMessage }];
    setDocChatMessages(nextMessages);
    setDocChatLoading(true);

    try {
      const response = await axios.post(`${API}/upload/chat`, {
        filename: analysis?.filename,
        analysis: analysis?.analysis,
        document_text: documentText,
        message: userMessage,
        history: nextMessages
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setDocChatMessages((prev) => [...prev, { role: 'assistant', content: response.data.response }]);
    } catch (error) {
      console.error('Document chat error:', error);
      toast.error(
        error.response?.data?.detail ||
        error.response?.data?.error ||
        'Failed to chat about this document'
      );
    } finally {
      setDocChatLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <ScrollArea className="flex-1">
        <div className="max-w-4xl mx-auto px-6 py-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="text-center mb-12">
              <h2
                className="text-4xl font-medium mb-4"
                style={{
                  fontFamily: "'Cormorant Garamond', serif",
                  color: '#D4AF37'
                }}
              >
                Document Bias Analysis
              </h2>
              <p className="text-base" style={{ color: '#94A3B8' }}>
                Upload a document and I'll analyze it for potential biases related to gender, race, religion, or other factors.
              </p>
            </div>

            {/* Upload Area */}
            {!analysis && (
              <div
                className="border-2 border-dashed rounded-md p-12 text-center transition-all duration-300"
                style={{
                  borderColor: file ? '#D4AF37' : 'rgba(255, 255, 255, 0.1)',
                  backgroundColor: 'rgba(255, 255, 255, 0.03)'
                }}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="*/*"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                  data-testid="file-upload-input"
                />

                {!file ? (
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer block"
                  >
                    <UploadSimple
                      size={64}
                      weight="duotone"
                      className="mx-auto mb-4"
                      style={{ color: '#D4AF37' }}
                    />
                    <p className="text-lg mb-2" style={{ color: '#F8FAFC' }}>
                      Click to upload document
                    </p>
                    <p
                      className="text-sm uppercase tracking-[0.2em]"
                      style={{
                        fontFamily: "'IBM Plex Mono', monospace",
                        color: '#475569'
                      }}
                    >
                      all file types supported
                    </p>
                  </label>
                ) : (
                  <div>
                    <FileText
                      size={64}
                      weight="duotone"
                      className="mx-auto mb-4"
                      style={{ color: '#D4AF37' }}
                    />
                    <p className="text-lg mb-2" style={{ color: '#F8FAFC' }}>
                      {file.name}
                    </p>
                    <p
                      className="text-sm mb-6"
                      style={{
                        fontFamily: "'IBM Plex Mono', monospace",
                        color: '#94A3B8'
                      }}
                    >
                      {(file.size / 1024).toFixed(2)} KB
                    </p>

                    <div className="flex gap-3 justify-center">
                      <Button
                        data-testid="analyze-button"
                        onClick={handleUpload}
                        disabled={loading}
                        className="gap-2 px-6 transition-all duration-300"
                        style={{
                          backgroundColor: loading ? '#475569' : '#D4AF37',
                          color: '#030712'
                        }}
                        onMouseEnter={(e) => {
                          if (!loading) {
                            e.target.style.backgroundColor = '#FBE689';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (!loading) {
                            e.target.style.backgroundColor = '#D4AF37';
                          }
                        }}
                      >
                        {loading ? (
                          <div
                            className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin"
                            style={{ borderColor: '#030712', borderTopColor: 'transparent' }}
                          />
                        ) : (
                          'Analyze Document'
                        )}
                      </Button>

                      <Button
                        onClick={handleReset}
                        disabled={loading}
                        variant="outline"
                        style={{
                          borderColor: 'rgba(255, 255, 255, 0.1)',
                          color: '#94A3B8'
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Analysis Results */}
            {analysis && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                data-testid="analysis-result"
              >
                <div
                  className="p-6 rounded-md border mb-6"
                  style={{
                    backgroundColor: '#0B101A',
                    borderColor: '#D4AF37'
                  }}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <CheckCircle size={24} weight="duotone" style={{ color: '#10B981' }} />
                    <h3
                      className="text-xl font-normal"
                      style={{
                        fontFamily: "'Cormorant Garamond', serif",
                        color: '#F8FAFC'
                      }}
                    >
                      Analysis Complete
                    </h3>
                  </div>

                  <div
                    className="mb-4 pb-4 border-b"
                    style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}
                  >
                    <p
                      className="text-xs uppercase tracking-[0.2em] mb-2"
                      style={{
                        fontFamily: "'IBM Plex Mono', monospace",
                        color: '#475569'
                      }}
                    >
                      Document
                    </p>
                    <p style={{ color: '#94A3B8' }}>{analysis.filename}</p>
                  </div>

                  <div>
                    <p
                      className="text-xs uppercase tracking-[0.2em] mb-3"
                      style={{
                        fontFamily: "'IBM Plex Mono', monospace",
                        color: '#475569'
                      }}
                    >
                      Athena's Analysis
                    </p>
                    <p
                      className="text-base leading-relaxed whitespace-pre-wrap"
                      style={{
                        fontFamily: "'Cormorant Garamond', serif",
                        color: '#F8FAFC'
                      }}
                    >
                      {analysis.analysis}
                    </p>
                  </div>
                </div>

                <Button
                  data-testid="upload-another-button"
                  onClick={handleReset}
                  className="w-full transition-all duration-300"
                  style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.03)',
                    color: '#D4AF37',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.06)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.03)';
                  }}
                >
                  Analyze Another Document
                </Button>

                <div
                  className="mt-6 p-4 rounded-md border"
                  style={{
                    backgroundColor: '#0B101A',
                    borderColor: 'rgba(255, 255, 255, 0.1)'
                  }}
                >
                  <p
                    className="text-xs uppercase tracking-[0.2em] mb-3"
                    style={{
                      fontFamily: "'IBM Plex Mono', monospace",
                      color: '#475569'
                    }}
                  >
                    Ask Athena About This Document
                  </p>

                  <div className="space-y-3 max-h-72 overflow-y-auto mb-3 pr-1">
                    {docChatMessages.length === 0 ? (
                      <p className="text-sm" style={{ color: '#94A3B8' }}>
                        Ask things like: "Rewrite this to remove biased phrasing", "Find loaded words", or "Summarize section 2."
                      </p>
                    ) : (
                      docChatMessages.map((msg, idx) => (
                        <div
                          key={`${msg.role}-${idx}`}
                          className={`p-3 rounded-md ${msg.role === 'user' ? 'ml-8' : 'mr-8'}`}
                          style={{
                            backgroundColor: msg.role === 'user' ? 'rgba(212, 175, 55, 0.1)' : 'rgba(255, 255, 255, 0.03)',
                            borderLeft: msg.role === 'user' ? '2px solid #D4AF37' : '2px solid rgba(255, 255, 255, 0.1)'
                          }}
                        >
                          <p className="text-sm whitespace-pre-wrap" style={{ color: '#F8FAFC' }}>
                            {msg.content}
                          </p>
                        </div>
                      ))
                    )}
                  </div>

                  <div className="flex gap-2 items-end">
                    <Textarea
                      value={docChatInput}
                      onChange={(e) => setDocChatInput(e.target.value)}
                      placeholder="Tell Athena what you want from this document..."
                      rows={2}
                      disabled={docChatLoading}
                      className="resize-none bg-transparent border"
                      style={{
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        color: '#F8FAFC'
                      }}
                    />
                    <Button
                      onClick={handleDocChatSend}
                      disabled={docChatLoading || !docChatInput.trim()}
                      className="px-4"
                      style={{
                        backgroundColor: docChatLoading || !docChatInput.trim() ? '#475569' : '#D4AF37',
                        color: '#030712'
                      }}
                    >
                      {docChatLoading ? (
                        <div
                          className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin"
                          style={{ borderColor: '#030712', borderTopColor: 'transparent' }}
                        />
                      ) : (
                        <PaperPlaneRight size={18} weight="bold" />
                      )}
                    </Button>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        </div>
      </ScrollArea>
    </div>
  );
};

export default DocumentUpload;
