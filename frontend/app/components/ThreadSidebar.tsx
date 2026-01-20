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
}

export default function ThreadSidebar({ onSelectThread, currentThreadId, refreshTrigger }: ThreadSidebarProps) {
  const { token } = useAuth();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
    <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <button
          onClick={handleNewChat}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          + New Chat
        </button>
      </div>

      {/* Threads List */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading && (
          <div className="text-gray-400 text-center py-8">
            Loading threads...
          </div>
        )}

        {error && (
          <div className="text-red-400 text-center py-8">
            {error}
          </div>
        )}

        {!loading && !error && threads.length === 0 && (
          <div className="text-gray-400 text-center py-8">
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
                ? 'bg-gray-800 border border-gray-700' 
                : 'hover:bg-gray-800/50'
              }
            `}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h3 className="text-white text-sm font-medium truncate">
                  {thread.title}
                </h3>
                <p className="text-gray-500 text-xs mt-1">
                  {thread.message_count} messages
                </p>
              </div>
              <button
                onClick={(e) => handleDeleteThread(thread.id, e)}
                className="ml-2 text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Delete thread"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* User Info */}
      <div className="p-4 border-t border-gray-800">
        <button
          onClick={() => {
            if (confirm('Are you sure you want to log out?')) {
              window.location.href = '/login';
            }
          }}
          className="w-full text-gray-400 hover:text-white text-sm transition-colors"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
