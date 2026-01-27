'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface GameState {
  board: string[];
  game_over: boolean;
  winner: string | null;
  available_moves: number[];
  message: string;
  ai_position?: number | null;
  ai_reasoning?: string;
}

export default function TicTacToePage() {
  const router = useRouter();
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiThinking, setAiThinking] = useState(false);
  const [showReasoning, setShowReasoning] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    
    // Start a new game
    startNewGame();
  }, []);

  const startNewGame = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8001/api/tictactoe/new', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to start new game');
      }

      const data = await response.json();
      setGameState(data);
    } catch (err: any) {
      setError(err.message);
      if (err.message.includes('401')) {
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const makeMove = async (position: number) => {
    if (!gameState || gameState.game_over || aiThinking) return;
    if (!gameState.available_moves.includes(position)) return;

    setAiThinking(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8001/api/tictactoe/move', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ position }),
      });

      if (!response.ok) {
        throw new Error('Failed to make move');
      }

      const data = await response.json();
      setGameState(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setAiThinking(false);
    }
  };

  const getCellSymbol = (index: number) => {
    if (!gameState) return '';
    const value = gameState.board[index];
    return value === ' ' ? '' : value;
  };

  const isCellAvailable = (index: number) => {
    return gameState?.available_moves.includes(index) && !gameState.game_over;
  };

  const getWinnerMessage = () => {
    if (!gameState || !gameState.game_over) return '';
    
    if (gameState.winner === 'X') {
      return '🎉 You Won! Congratulations!';
    } else if (gameState.winner === 'O') {
      return '🤖 AI Won! Better luck next time!';
    } else if (gameState.winner === 'Draw') {
      return '🤝 It\'s a Draw!';
    }
    return '';
  };

  if (loading && !gameState) {
    return (
      <div className="h-full bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading game...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-hidden bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex flex-col">
      <div className="flex-1 overflow-y-auto py-8 px-4">
        <div className="max-w-4xl mx-auto">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <span className="text-2xl font-bold text-blue-600">You (X)</span>
              <span className="mx-4 text-gray-400">vs</span>
              <span className="text-2xl font-bold text-red-600">AI (O)</span>
            </div>
            <button
              onClick={startNewGame}
              disabled={loading}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
            >
              New Game
            </button>
          </div>

          {gameState?.message && (
            <div className={`p-3 rounded-lg mb-4 ${
              gameState.game_over 
                ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                : 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
            }`}>
              {gameState.message}
            </div>
          )}

          {gameState?.game_over && (
            <div className="text-center p-4 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg text-white font-bold text-xl mb-4">
              {getWinnerMessage()}
            </div>
          )}

          {aiThinking && (
            <div className="flex items-center justify-center p-3 bg-gray-100 dark:bg-gray-700 rounded-lg mb-4">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600 mr-3"></div>
              <span className="text-gray-700 dark:text-gray-300">AI is thinking...</span>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-lg mb-4">
              {error}
            </div>
          )}
        </div>

        {/* Game Board */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-6">
          <div className="grid grid-cols-3 gap-4 max-w-md mx-auto">
            {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((index) => {
              const symbol = getCellSymbol(index);
              const isAvailable = isCellAvailable(index);
              const isWinningCell = false; // Could add winning line highlighting

              return (
                <button
                  key={index}
                  onClick={() => makeMove(index)}
                  disabled={!isAvailable || aiThinking}
                  className={`
                    aspect-square rounded-lg text-5xl font-bold
                    transition-all duration-200 transform
                    ${symbol === 'X' ? 'text-blue-600' : ''}
                    ${symbol === 'O' ? 'text-red-600' : ''}
                    ${isAvailable && !aiThinking
                      ? 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 hover:scale-105 cursor-pointer'
                      : 'bg-gray-50 dark:bg-gray-800 cursor-not-allowed'
                    }
                    ${symbol ? 'shadow-inner' : 'shadow-md'}
                    ${isWinningCell ? 'ring-4 ring-yellow-400' : ''}
                  `}
                >
                  {symbol}
                </button>
              );
            })}
          </div>

          {/* Position Reference */}
          <div className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
            <p>Board positions: 0-8 (top-left to bottom-right)</p>
          </div>
        </div>

        {/* AI Reasoning (Optional) */}
        {gameState?.ai_reasoning && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <button
              onClick={() => setShowReasoning(!showReasoning)}
              className="flex items-center justify-between w-full text-left"
            >
              <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
                🤖 AI Reasoning
              </h3>
              <span className="text-gray-500">
                {showReasoning ? '▼' : '▶'}
              </span>
            </button>
            
            {showReasoning && (
              <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                  {gameState.ai_reasoning}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-3">
            📖 How to Play
          </h3>
          <ul className="space-y-2 text-gray-600 dark:text-gray-400">
            <li>• You play as <strong className="text-blue-600">X</strong>, AI plays as <strong className="text-red-600">O</strong></li>
            <li>• Click on an empty cell to make your move</li>
            <li>• The AI will automatically respond with its move</li>
            <li>• Get three in a row (horizontal, vertical, or diagonal) to win!</li>
            <li>• The AI uses a Langchain agent to analyze the board and make strategic decisions</li>
          </ul>
        </div>

        {/* Back Button */}
        <div className="mt-6 text-center">
          <button
            onClick={() => router.push('/')}
            className="px-6 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
          >
            ← Back to Home
          </button>
        </div>
        </div>
      </div>
    </div>
  );
}
