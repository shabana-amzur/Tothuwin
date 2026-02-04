"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface Thread {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface ThreadSidebarProps {
  onSelectThread: (threadId: number | null) => void;
  currentThreadId: number | null;
  refreshTrigger?: number;
  onNavigate?: (path: string) => void;
  onToggleImageValidation?: () => void;
  onFeatureSelect?: (feature: 'sql' | 'excel' | 'game' | 'rag') => void;
}

export default function ThreadSidebar({ onSelectThread, currentThreadId, refreshTrigger, onNavigate, onToggleImageValidation, onFeatureSelect }: ThreadSidebarProps) {
  const { token } = useAuth();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isChatsOpen, setIsChatsOpen] = useState(true); // Accordion state

  const loadThreads = async () => {
    if (!token) return;

    try {
      setLoading(true);
      const response = await fetch('http://localhost:8001/api/threads', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load threads');
      }

      const data = await response.json();
      setThreads(data);
      setError(null);
    } catch (err) {
      console.error('Error loading threads:', err);
      setError('Failed to load threads');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadThreads();
  }, [token, refreshTrigger]);

  const handleNewChat = () => {
    // Navigate to main chat page first if on a different page
    if (onNavigate) {
      onNavigate('/');
    }
    // Then reset to new chat
    onSelectThread(null);
  };

  const handleDeleteThread = async (threadId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!confirm('Are you sure you want to delete this thread?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8001/api/threads/${threadId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete thread');
      }

      // Reload threads
      await loadThreads();
      
      // If deleted thread was selected, deselect it
      if (currentThreadId === threadId) {
        onSelectThread(null);
      }
    } catch (err) {
      console.error('Error deleting thread:', err);
      alert('Failed to delete thread');
    }
  };

  return (
    <div className="w-64 bg-[#f3f3f3] dark:bg-[#181818] flex flex-col h-screen">
      {/* Sticky Header with Feature Buttons */}
      <div className="sticky top-0 z-10 bg-[#f3f3f3] dark:bg-[#181818] p-4 space-y-2">
        <button
          onClick={handleNewChat}
          className="w-full bg-[#10a37f] hover:bg-[#0d8c6f] text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
        >
          <span>✏️</span>
          <span>New Chat</span>
        </button>
        
        {/* Feature Buttons */}
        <button
          onClick={() => onFeatureSelect?.('sql')}
          className="w-full bg-[#ec6438]/80 hover:bg-[#ec6438] text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-start gap-2"
        >
          <span>📊</span>
          <span>SQL Query</span>
        </button>
        
        <button
          onClick={() => onFeatureSelect?.('excel')}
          className="w-full bg-[#ec6438]/80 hover:bg-[#ec6438] text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-start gap-2"
        >
          <span>📈</span>
          <span>Excel Analysis</span>
        </button>
        
        <button
          onClick={() => onToggleImageValidation?.()}
          className="w-full bg-[#ec6438]/80 hover:bg-[#ec6438] text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-start gap-2"
        >
          <span>🔍</span>
          <span>Image Validation</span>
        </button>
        
        <button
          onClick={() => onFeatureSelect?.('game')}
          className="w-full bg-[#ec6438]/80 hover:bg-[#ec6438] text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-start gap-2"
        >
          <span>🎮</span>
          <span>Tic-Tac-Toe</span>
        </button>
        
        <button
          onClick={() => onFeatureSelect?.('rag')}
          className="w-full bg-[#ec6438]/80 hover:bg-[#ec6438] text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-start gap-2"
        >
          <span>📚</span>
          <span>Document Q&A</span>
        </button>
      </div>

      {/* Scrollable Threads Section */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 pt-3">
          {/* Accordion Header */}
          <button
            onClick={() => setIsChatsOpen(!isChatsOpen)}
            className="w-full flex items-center justify-between text-xs font-semibold text-gray-800 dark:text-gray-300 uppercase tracking-wider mb-3 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <span>Your chats</span>
            <svg
              className={`w-4 h-4 transition-transform duration-200 ${isChatsOpen ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {/* Collapsible Content */}
          {isChatsOpen && (
            <>
        {loading && (
          <div className="text-gray-600 dark:text-gray-400 text-center py-8">
            Loading threads...
          </div>
        )}

        {error && (
          <div className="text-red-600 dark:text-red-400 text-center py-8">
            {error}
          </div>
        )}

        {!loading && !error && threads.length === 0 && (
          <div className="text-gray-600 dark:text-gray-400 text-center py-8">
            No threads yet. Start a new chat!
          </div>
        )}

        {!loading && !error && threads.map((thread) => (
          <div
            key={thread.id}
            onClick={() => onSelectThread(thread.id)}
            className={`
              mb-2 p-3 rounded-lg cursor-pointer transition-colors group
              ${currentThreadId === thread.id 
                ? 'bg-gray-300 dark:bg-black' 
                : 'hover:bg-gray-200/50 dark:hover:bg-gray-800/50'
              }
            `}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h3 className="text-gray-900 dark:text-gray-200 text-sm font-medium truncate">
                  {thread.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-xs mt-1">
                  {thread.message_count} messages
                </p>
              </div>
              <button
                onClick={(e) => handleDeleteThread(thread.id, e)}
                className="ml-2 text-gray-500 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Delete thread"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        ))}
            </>
          )}
        </div>
      </div>

      {/* Sticky User Info Footer */}
      <div className="sticky bottom-0 bg-[#f3f3f3] dark:bg-[#181818] p-4">
        <button
          onClick={() => {
            if (confirm('Are you sure you want to log out?')) {
              window.location.href = '/login';
            }
          }}
          className="w-full text-gray-800 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white text-sm transition-colors"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
