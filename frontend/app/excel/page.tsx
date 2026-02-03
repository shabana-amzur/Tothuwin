'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface ExcelFile {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  rows: number;
  columns: number;
  column_names: string[];
  sheet_names?: string[];
  created_at: string;
}

interface ExcelSummary {
  rows: number;
  columns: number;
  column_names: string[];
  column_types: Record<string, string>;
  sample_data: Record<string, any>[];
  sheet_names?: string[];
}

export default function ExcelPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [files, setFiles] = useState<ExcelFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<ExcelFile | null>(null);
  const [summary, setSummary] = useState<ExcelSummary | null>(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [selectedSheet, setSelectedSheet] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [isLoadingSummary, setIsLoadingSummary] = useState(false);
  const [error, setError] = useState('');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [googleSheetUrl, setGoogleSheetUrl] = useState('');
  const [isLoadingSheet, setIsLoadingSheet] = useState(false);

  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const validExtensions = ['.xlsx', '.xls', '.xlsm', '.csv'];
      const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (!validExtensions.includes(fileExt)) {
        setError('Invalid file type. Please upload Excel (.xlsx, .xls, .xlsm) or CSV files.');
        return;
      }
      
      if (file.size > 50 * 1024 * 1024) {
        setError('File too large. Maximum size is 50MB.');
        return;
      }
      
      setUploadFile(file);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) return;
    
    setIsUploading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      
      const response = await fetch('http://localhost:8001/api/excel/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }
      
      const data = await response.json();
      setFiles([data, ...files]);
      setUploadFile(null);
      
      // Auto-select the uploaded file
      setSelectedFile(data);
      await loadFileSummary(data.id);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const loadFileSummary = async (fileId: number, sheetName?: string) => {
    setIsLoadingSummary(true);
    setError('');
    
    try {
      const url = sheetName 
        ? `http://localhost:8001/api/excel/${fileId}/summary?sheet_name=${encodeURIComponent(sheetName)}`
        : `http://localhost:8001/api/excel/${fileId}/summary`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to load summary');
      
      const data = await response.json();
      setSummary(data);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load summary');
    } finally {
      setIsLoadingSummary(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!selectedFile || !question.trim()) return;
    
    setIsAsking(true);
    setError('');
    
    try {
      const response = await fetch(`http://localhost:8001/api/excel/${selectedFile.id}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          question: question.trim(),
          sheet_name: selectedSheet
        })
      });
      
      if (!response.ok) throw new Error('Failed to get answer');
      
      const data = await response.json();
      setAnswer(data.answer);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get answer');
    } finally {
      setIsAsking(false);
    }
  };

  const handleLoadGoogleSheet = async () => {
    if (!googleSheetUrl.trim()) return;
    
    setIsLoadingSheet(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:8001/api/excel/google-sheet', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          url: googleSheetUrl.trim(),
          sheet_name: null
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load Google Sheet');
      }
      
      const data = await response.json();
      setFiles([data, ...files]);
      setGoogleSheetUrl('');
      
      // Auto-select the loaded sheet
      setSelectedFile(data);
      await loadFileSummary(data.id);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load Google Sheet');
    } finally {
      setIsLoadingSheet(false);
    }
  };

  const handleDeleteFile = async (fileId: number, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent file selection when clicking delete
    
    if (!confirm('Are you sure you want to delete this file?')) return;
    
    setError('');
    
    try {
      const response = await fetch(`http://localhost:8001/api/excel/${fileId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete file');
      }
      
      // Remove from files list
      setFiles(files.filter(f => f.id !== fileId));
      
      // Clear selection if deleted file was selected
      if (selectedFile?.id === fileId) {
        setSelectedFile(null);
        setSummary(null);
        setAnswer('');
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete file');
    }
  };

  const exampleQuestions = [
    "What is the total sum of all values in the first column?",
    "How many rows contain data?",
    "What are the average values for each numeric column?",
    "Show me the top 5 records by value",
    "What is the distribution of data across different categories?"
  ];

  if (!user) return null;

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 overflow-hidden">
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <div className="bg-[#181818] rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-white mb-4">Upload Excel/CSV or Load Google Sheet</h2>
          
          {/* File Upload */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-300 mb-2">Upload File</h3>
            <div className="flex items-center space-x-4">
              <input
                type="file"
                accept=".xlsx,.xls,.xlsm,.csv"
                onChange={handleFileSelect}
                className="block w-full text-sm text-gray-400
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-[#ec6438] file:text-white
                  hover:file:opacity-90 file:cursor-pointer file:transition-all"
                style={{ colorScheme: 'dark' }}
              />
              
              <button
                onClick={handleUpload}
                disabled={!uploadFile || isUploading}
                style={{ backgroundColor: '#ec6438' }}
                className="px-6 py-2 text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap transition-all"
              >
                {isUploading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
            <p className="text-gray-400 text-sm mt-2">
              Supported: Excel (.xlsx, .xls, .xlsm) and CSV (.csv) • Max: 50MB
            </p>
          </div>
          
          {/* Google Sheets */}
          <div>
            <h3 className="text-sm font-medium text-gray-300 mb-2">Or Load from Google Sheets</h3>
            <div className="flex items-center space-x-4">
              <input
                type="url"
                value={googleSheetUrl}
                onChange={(e) => setGoogleSheetUrl(e.target.value)}
                placeholder="Paste Google Sheets link here (must be publicly accessible)"
                className="flex-1 bg-[#0f0f0f] text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              
              <button
                onClick={handleLoadGoogleSheet}
                disabled={!googleSheetUrl.trim() || isLoadingSheet}
                style={{ backgroundColor: '#ec6438' }}
                className="px-6 py-2 text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap transition-all"
              >
                {isLoadingSheet ? 'Loading...' : 'Load Sheet'}
              </button>
            </div>
            <p className="text-gray-400 text-sm mt-2">
              💡 Make sure the Google Sheet is set to "Anyone with the link can view"
            </p>
          </div>
        </div>

        {error && (
          <div className="bg-[#0f0f0f] text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* File List */}
          <div className="lg:col-span-1">
            <div className="bg-[#181818] rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Your Files</h2>
              
              {files.length === 0 ? (
                <p className="text-gray-400 text-sm">No files uploaded yet</p>
              ) : (
                <div className="space-y-2">
                  {files.map((file) => (
                    <div
                      key={file.id}
                      className={`w-full text-left p-3 rounded-lg transition-all flex items-center justify-between group ${
                        selectedFile?.id === file.id
                          ? 'bg-[#ec6438] text-white'
                          : 'bg-[#0f0f0f] text-gray-300 hover:bg-[#252525]'
                      }`}
                    >
                      <button
                        onClick={() => {
                          setSelectedFile(file);
                          setSummary(null);
                          setAnswer('');
                          loadFileSummary(file.id);
                        }}
                        className="flex-1 text-left overflow-hidden"
                      >
                        <div className="font-medium truncate" title={file.original_filename}>
                          {file.original_filename}
                        </div>
                        <div className="text-xs opacity-75 mt-1">
                          {file.rows} rows × {file.columns} cols
                        </div>
                      </button>
                      <button
                        onClick={(e) => handleDeleteFile(file.id, e)}
                        className="ml-2 p-2 rounded hover:bg-red-600 opacity-0 group-hover:opacity-100 transition-all flex-shrink-0"
                        title="Delete file"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {selectedFile ? (
              <>
                {/* File Info */}
                <div className="bg-[#181818] rounded-lg p-6">
                  <h2 className="text-xl font-semibold text-white mb-4">
                    {selectedFile.original_filename}
                  </h2>
                  
                  {selectedFile.sheet_names && selectedFile.sheet_names.length > 1 && (
                    <div className="mb-4">
                      <label className="block text-gray-400 text-sm mb-2">Select Sheet:</label>
                      <select
                        value={selectedSheet || ''}
                        onChange={(e) => {
                          setSelectedSheet(e.target.value);
                          loadFileSummary(selectedFile.id, e.target.value);
                        }}
                        className="w-full bg-[#0f0f0f] text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      >
                        {selectedFile.sheet_names.map((sheet) => (
                          <option key={sheet} value={sheet}>{sheet}</option>
                        ))}
                      </select>
                    </div>
                  )}
                  
                  {isLoadingSummary ? (
                    <div className="text-gray-400">Loading data preview...</div>
                  ) : summary && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">Rows:</span>
                          <span className="text-white ml-2 font-semibold">{summary.rows}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Columns:</span>
                          <span className="text-white ml-2 font-semibold">{summary.columns}</span>
                        </div>
                      </div>
                      
                      <div>
                        <h3 className="text-gray-400 text-sm mb-2">Columns:</h3>
                        <div className="flex flex-wrap gap-2">
                          {summary.column_names.map((col) => (
                            <span key={col} className="bg-[#0f0f0f] text-gray-300 px-3 py-1 rounded-full text-xs">
                              {col}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      {summary.sample_data && summary.sample_data.length > 0 && (
                        <div>
                          <h3 className="text-gray-400 text-sm mb-2">Preview (first 5 rows):</h3>
                          <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                              <thead className="bg-[#0f0f0f]">
                                <tr>
                                  {summary.column_names.map((col) => (
                                    <th key={col} className="px-3 py-2 text-gray-300">{col}</th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {summary.sample_data.map((row, idx) => (
                                  <tr key={idx} className="border-t border-[#0f0f0f]">
                                    {summary.column_names.map((col) => (
                                      <td key={col} className="px-3 py-2 text-gray-400">
                                        {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Ask Question */}
                <div className="bg-[#181818] rounded-lg p-6">
                  <h2 className="text-xl font-semibold text-white mb-4">Ask Questions</h2>
                  
                  <div className="space-y-4">
                    <div>
                      <textarea
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Ask a question about your data..."
                        className="w-full bg-[#0f0f0f] text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                        rows={3}
                      />
                    </div>
                    
                    <button
                      onClick={handleAskQuestion}
                      disabled={!question.trim() || isAsking}
                      style={{ backgroundColor: '#ec6438' }}
                      className="w-full px-6 py-3 text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all"
                    >
                      {isAsking ? 'Analyzing...' : 'Ask Question'}
                    </button>
                    
                    <div className="text-gray-400 text-xs">
                      <p className="font-medium mb-2">Example questions:</p>
                      <ul className="space-y-1">
                        {exampleQuestions.map((q, idx) => (
                          <li 
                            key={idx}
                            onClick={() => setQuestion(q)}
                            className="cursor-pointer hover:text-orange-400 transition-colors"
                          >
                            • {q}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  {answer && (
                    <div className="mt-6 bg-[#0f0f0f] rounded-lg p-4">
                      <h3 className="text-orange-400 font-semibold mb-2">Answer:</h3>
                      <div className="text-gray-200 whitespace-pre-wrap">{answer}</div>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="bg-[#181818] rounded-lg p-12 text-center">
                <div className="text-6xl mb-4">📊</div>
                <h2 className="text-2xl font-semibold text-white mb-2">
                  Select a File
                </h2>
                <p className="text-gray-400">
                  Choose a file from your uploaded files or upload a new one above
                </p>
              </div>
            )}
          </div>
        </div>
        </div>
      </div>
    </div>
  );
}
