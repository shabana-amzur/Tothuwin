'use client';

import { useState, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import MarkdownRenderer from './MarkdownRenderer';

interface DocumentQAResult {
  success: boolean;
  question: string;
  answer: string;
  document_name?: string;
  error?: string;
}

export default function DocumentQAPage() {
  const { token, logout } = useAuth();
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<DocumentQAResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadedDocuments, setUploadedDocuments] = useState<string[]>([]);
  const [currentThreadId, setCurrentThreadId] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const suggestedQuestions = [
    "What is the main topic of this document?",
    "Can you summarize the key points?",
    "What are the important dates or numbers mentioned?",
    "Who are the main people or entities mentioned?"
  ];

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const allowedTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      const allowedExts = ['.pdf', '.txt', '.docx'];
      
      if (!allowedTypes.includes(file.type) && !allowedExts.includes(fileExt)) {
        alert('Supported files: PDF, TXT, DOCX only');
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        alert('File size must be less than 50MB');
        return;
      }
      setSelectedFile(file);
      
      // Auto-upload the file
      await uploadDocument(file);
    }
  };

  const uploadDocument = async (file?: File) => {
    const fileToUpload = file || selectedFile;
    if (!fileToUpload) return;

    setIsUploading(true);

    try {
      let threadId = currentThreadId;
      if (!threadId) {
        const createThreadResponse = await fetch('http://localhost:8001/api/threads/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            title: `Document Q&A: ${fileToUpload.name}`
          }),
        });
        
        if (!createThreadResponse.ok) {
          throw new Error('Failed to create session');
        }
        
        const threadData = await createThreadResponse.json();
        threadId = threadData.id;
        setCurrentThreadId(threadId);
      }
      
      const formData = new FormData();
      formData.append('file', fileToUpload);
      
      const url = new URL('http://localhost:8001/api/documents/upload');
      url.searchParams.append('thread_id', threadId!.toString());

      const response = await fetch(url.toString(), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to upload document');
      }

      setUploadedDocuments(prev => [...prev, fileToUpload.name]);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      alert(`✅ ${fileToUpload.name} uploaded successfully!`);
    } catch (error) {
      console.error('Upload error:', error);
      alert(`❌ Failed to upload: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsUploading(false);
    }
  };

  const askQuestion = async (questionText: string) => {
    if (!questionText.trim() || isLoading) return;

    if (!currentThreadId || uploadedDocuments.length === 0) {
      alert('Please upload a document first');
      return;
    }

    setIsLoading(true);
    setResult(null);
    setQuestion(questionText);

    try {
      const response = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ 
          message: questionText.trim(),
          thread_id: currentThreadId,
          model: 'rag'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        if (response.status === 401) {
          logout();
          throw new Error('Session expired');
        }
        throw new Error(errorData.detail || 'Failed to get answer');
      }

      const data = await response.json();
      setResult({
        success: true,
        question: questionText.trim(),
        answer: data.message,
        document_name: uploadedDocuments[uploadedDocuments.length - 1]
      });
    } catch (error) {
      console.error('Error:', error);
      setResult({
        success: false,
        question: questionText.trim(),
        answer: '',
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    askQuestion(question);
  };

  const clearSession = () => {
    setCurrentThreadId(null);
    setUploadedDocuments([]);
    setResult(null);
    setQuestion('');
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-teal-900 via-gray-900 to-gray-800">
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Upload & Info */}
            <div className="lg:col-span-1 space-y-6 lg:sticky lg:top-6 lg:self-start">
              {/* Upload Section */}
              <div className="bg-[#181818] rounded-lg p-6">
                <h2 className="text-xl font-semibold text-white mb-4">📤 Upload Document</h2>
                
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.txt,.docx"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className="w-full bg-[#181818] border-2 border-[#ec6438] hover:bg-[#ec6438]/10 text-white px-4 py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed mb-4"
                >
                  {isUploading ? '📤 Uploading...' : (selectedFile ? '📄 Change File' : '📎 Select File')}
                </button>

                {uploadedDocuments.length > 0 && (
                  <div className="border-t border-gray-700 pt-4">
                    <p className="text-sm text-gray-400 mb-2">Uploaded Documents:</p>
                    <div className="space-y-2">
                      {uploadedDocuments.map((doc, idx) => (
                        <div key={idx} className="flex items-center space-x-2 text-sm text-teal-400">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span className="truncate">{doc}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {uploadedDocuments.length > 0 && (
                  <button
                    onClick={clearSession}
                    className="w-full mt-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm transition-colors"
                  >
                    🗑️ Clear Session
                  </button>
                )}
              </div>

              {/* Supported Formats */}
              <div className="bg-[#181818] rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4">📄 Supported Formats</h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li className="flex items-center">
                    <span className="text-red-400 mr-2">•</span>
                    <span><strong>PDF</strong> - Portable Document Format</span>
                  </li>
                  <li className="flex items-center">
                    <span className="text-blue-400 mr-2">•</span>
                    <span><strong>TXT</strong> - Plain Text Files</span>
                  </li>
                  <li className="flex items-center">
                    <span className="text-purple-400 mr-2">•</span>
                    <span><strong>DOCX</strong> - Microsoft Word</span>
                  </li>
                </ul>
                <p className="text-xs text-gray-500 mt-4">Max file size: 50 MB</p>
              </div>

              {/* How It Works */}
              <div className="bg-[#181818] rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4">🔍 How It Works</h3>
                <ul className="space-y-3 text-sm text-gray-300">
                  <li className="flex items-start">
                    <span className="text-teal-400 mr-2">•</span>
                    <span><strong>Embeddings:</strong> HuggingFace (FREE, local)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-teal-400 mr-2">•</span>
                    <span><strong>Vector DB:</strong> ChromaDB similarity search</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-teal-400 mr-2">•</span>
                    <span><strong>Grounding:</strong> Answers ONLY from documents</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-teal-400 mr-2">•</span>
                    <span><strong>No Hallucination:</strong> Strict citations</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Right Column - Question & Results */}
            <div className="lg:col-span-2 space-y-6">
              {/* Question Form */}
              <form onSubmit={handleFormSubmit} className="bg-[#181818] rounded-lg p-6">
                <h2 className="text-xl font-semibold text-white mb-4">💬 Ask Question</h2>
                
                <div className="mb-4">
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Type your question about the uploaded document..."
                    disabled={isLoading || uploadedDocuments.length === 0}
                    rows={4}
                    className="w-full bg-[#0f0f0f] text-white border border-teal-800 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-600 disabled:opacity-50 disabled:cursor-not-allowed resize-none"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading || !question.trim() || uploadedDocuments.length === 0}
                  className="w-full bg-[#ec6438] hover:bg-[#d65430] disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  {isLoading ? '⏳ Searching document...' : '🔍 Get Answer'}
                </button>

                {/* Suggested Questions */}
                {uploadedDocuments.length > 0 && !result && (
                  <div className="mt-6">
                    <p className="text-sm text-gray-400 mb-3">💡 Suggested questions:</p>
                    <div className="grid grid-cols-1 gap-2">
                      {suggestedQuestions.map((q, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => askQuestion(q)}
                          disabled={isLoading}
                          className="text-left bg-teal-900/30 hover:bg-teal-900/50 border border-teal-700 rounded-lg px-4 py-2 text-sm text-teal-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </form>

              {/* Results */}
              {result && (
                <div className="bg-[#181818] rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">
                    {result.success ? '✅ Answer' : '❌ Error'}
                  </h3>

                  {result.success ? (
                    <div className="space-y-4">
                      <div className="bg-[#0f0f0f] rounded-lg p-3">
                        <p className="text-xs text-gray-500 mb-2">Question:</p>
                        <p className="text-white text-sm">{result.question}</p>
                      </div>

                      <div className="bg-teal-900/20 rounded-lg p-4">
                        <p className="text-xs text-teal-400 mb-3">
                          Answer from: {result.document_name}
                        </p>
                        <div className="text-gray-100 text-sm leading-relaxed markdown-content">
                          <style jsx>{`
                            .markdown-content :global(p) {
                              margin: 0 0 1em 0;
                              padding: 0;
                            }
                            .markdown-content :global(ul),
                            .markdown-content :global(ol) {
                              margin: 0 0 1em 0;
                              padding-left: 1.5em;
                            }
                            .markdown-content :global(li) {
                              margin: 0.5em 0;
                              padding: 0;
                            }
                            .markdown-content :global(h1),
                            .markdown-content :global(h2),
                            .markdown-content :global(h3),
                            .markdown-content :global(h4) {
                              margin: 1em 0 0.5em 0;
                              padding: 0;
                            }
                            .markdown-content :global(strong) {
                              font-weight: 600;
                            }
                          `}</style>
                          <MarkdownRenderer content={result.answer} />
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
                      <p className="text-red-400">{result.error}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
