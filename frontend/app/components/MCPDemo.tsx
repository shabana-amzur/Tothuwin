'use client';

import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface MCPResource {
  uri: string;
  name: string;
  description: string;
  mimeType?: string;
  content?: string;
}

interface MCPTool {
  name: string;
  description: string;
  inputSchema: any;
}

export default function MCPDemo() {
  const { token } = useAuth();
  const [resources, setResources] = useState<MCPResource[]>([]);
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [selectedResource, setSelectedResource] = useState<MCPResource | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'resources' | 'tools'>('chat');

  const exampleQuestions = [
    "What products does the company offer?",
    "How do I use Excel analysis?",
    "Search for information about SQL",
    "Get statistics for user ID 1",
    "Calculate 42 * 15 + 100",
    "Generate a usage report"
  ];

  const loadResources = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/mcp/resources', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setResources(data.resources);
      }
    } catch (error) {
      console.error('Error loading resources:', error);
    }
  };

  const loadTools = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/mcp/tools', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setTools(data.tools);
      }
    } catch (error) {
      console.error('Error loading tools:', error);
    }
  };

  const loadResourceDetails = async (uri: string) => {
    try {
      const response = await fetch(`http://localhost:8001/api/mcp/resources/${encodeURIComponent(uri)}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setSelectedResource(data.resource);
      }
    } catch (error) {
      console.error('Error loading resource:', error);
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    setIsLoading(true);
    setAnswer('');

    try {
      const response = await fetch('http://localhost:8001/api/mcp/chat', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: question.trim(),
          use_mcp: true
        })
      });

      const data = await response.json();
      if (data.success) {
        setAnswer(data.answer);
      } else {
        setAnswer('Error: ' + (data.detail || 'Unknown error'));
      }
    } catch (error) {
      setAnswer('Error: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 overflow-y-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            🤖 MCP (Model Context Protocol) Demo
          </h1>
          <p className="text-gray-400">
            Explore how AI agents use structured context and tools via MCP
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-700">
          <div className="flex space-x-4">
            {(['chat', 'resources', 'tools'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => {
                  setActiveTab(tab);
                  if (tab === 'resources' && resources.length === 0) loadResources();
                  if (tab === 'tools' && tools.length === 0) loadTools();
                }}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === tab
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h2 className="text-xl font-semibold text-white mb-4">
                💬 Chat with MCP Agent
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Your Question:
                  </label>
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask anything... The agent has access to company knowledge, tools, and more!"
                    className="w-full bg-gray-700 text-white rounded-lg px-4 py-3 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    rows={3}
                  />
                </div>

                <button
                  onClick={askQuestion}
                  disabled={isLoading || !question.trim()}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {isLoading ? 'Processing...' : 'Ask MCP Agent'}
                </button>

                {/* Example Questions */}
                <div>
                  <p className="text-sm text-gray-400 mb-2">Try these examples:</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {exampleQuestions.map((q, idx) => (
                      <button
                        key={idx}
                        onClick={() => setQuestion(q)}
                        className="text-left text-sm text-gray-300 hover:text-blue-400 bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded transition-colors"
                      >
                        💡 {q}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Answer */}
            {answer && (
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-semibold text-green-400 mb-3">
                  ✨ MCP Agent Response:
                </h3>
                <div className="text-gray-200 whitespace-pre-wrap">{answer}</div>
              </div>
            )}
          </div>
        )}

        {/* Resources Tab */}
        {activeTab === 'resources' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h2 className="text-xl font-semibold text-white mb-4">
                📚 Available Resources
              </h2>
              <div className="space-y-3">
                {resources.map((resource) => (
                  <button
                    key={resource.uri}
                    onClick={() => loadResourceDetails(resource.uri)}
                    className="w-full text-left p-4 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                  >
                    <div className="font-medium text-blue-400">{resource.name}</div>
                    <div className="text-sm text-gray-400 mt-1">{resource.description}</div>
                    <div className="text-xs text-gray-500 mt-2 font-mono">{resource.uri}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h2 className="text-xl font-semibold text-white mb-4">
                📄 Resource Content
              </h2>
              {selectedResource ? (
                <div className="space-y-3">
                  <div>
                    <div className="text-sm text-gray-400">Name:</div>
                    <div className="text-white font-medium">{selectedResource.name}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400">URI:</div>
                    <div className="text-blue-400 font-mono text-sm">{selectedResource.uri}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400 mb-2">Content:</div>
                    <div className="bg-gray-900 rounded p-4 text-gray-300 text-sm whitespace-pre-wrap max-h-96 overflow-y-auto">
                      {selectedResource.content}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-gray-400 text-center py-8">
                  Select a resource to view its content
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tools Tab */}
        {activeTab === 'tools' && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold text-white mb-4">
              🛠️ Available Tools
            </h2>
            <div className="space-y-4">
              {tools.map((tool) => (
                <div key={tool.name} className="p-4 bg-gray-700 rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-medium text-green-400">{tool.name}</div>
                    <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                      Tool
                    </span>
                  </div>
                  <div className="text-gray-300 mb-3">{tool.description}</div>
                  <details className="text-sm">
                    <summary className="cursor-pointer text-gray-400 hover:text-gray-300">
                      View Input Schema
                    </summary>
                    <pre className="mt-2 bg-gray-900 rounded p-3 text-gray-300 text-xs overflow-x-auto">
                      {JSON.stringify(tool.inputSchema, null, 2)}
                    </pre>
                  </details>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
