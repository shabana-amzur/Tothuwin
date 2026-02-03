'use client';

import { useState, useEffect } from 'react';

interface GameState {
  board: string[];
  game_over: boolean;
  winner: string | null;
  available_moves: number[];
  message: string;
  ai_position?: number | null;
  ai_reasoning?: string;
}

interface TicTacToeEmbeddedProps {
  token: string;
}

export default function TicTacToeEmbedded({ token }: TicTacToeEmbeddedProps) {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [aiThinking, setAiThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    startNewGame();
  }, []);

  const startNewGame = async () => {
    setError(null);
    
    if (!token) {
      setError('Please log in to play the game');
      return;
    }
    
    try {
      const response = await fetch('http://localhost:8001/api/tictactoe/new', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to start game: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      setGameState(data);
    } catch (err: any) {
      console.error('Game start error:', err);
      setError(err.message || 'Failed to connect to game server');
    }
  };

  const makeMove = async (position: number) => {
    if (!gameState || gameState.game_over || aiThinking) return;
    if (!gameState.available_moves.includes(position)) return;

    setAiThinking(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8001/api/tictactoe/move', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ position }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Move failed: ${response.status}`);
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
      return '🎉 You Won!';
    } else if (gameState.winner === 'O') {
      return '🤖 AI Won!';
    } else if (gameState.winner === 'Draw') {
      return '🤝 Draw!';
    }
    return '';
  };

  if (!gameState) {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-800 dark:to-gray-700 rounded-lg p-6">
        {error ? (
          <div className="text-center">
            <div className="text-red-500 text-4xl mb-3">⚠️</div>
            <p className="text-sm text-red-600 dark:text-red-400 mb-3">{error}</p>
            <button
              onClick={startNewGame}
              className="px-4 py-2 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition-colors"
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-3"></div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Loading game...</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-800 dark:to-gray-700 rounded-lg p-6 shadow-lg">
      {/* Header */}
      <div className="text-center mb-4">
        <h3 className="text-2xl font-bold text-gray-800 dark:text-white mb-1">
          🎮 Tic-Tac-Toe
        </h3>
        <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
          <span className="font-semibold text-blue-600">You (X)</span> vs <span className="font-semibold text-red-600">AI (O)</span>
        </div>
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('New Game button clicked (embedded)');
            startNewGame();
          }}
          disabled={!token}
          style={{ backgroundColor: '#ec6438' }}
          className="px-4 py-1.5 text-white text-sm rounded-lg hover:opacity-90 disabled:bg-gray-400 disabled:cursor-not-allowed cursor-pointer transition-all z-10 relative shadow-lg"
        >
          New Game
        </button>
      </div>

      {/* Status Messages */}
      {gameState.game_over && (
        <div className="text-center p-3 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg text-white font-bold mb-4">
          {getWinnerMessage()}
        </div>
      )}

      {aiThinking && (
        <div className="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg mb-4">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600 mr-2"></div>
          <span className="text-sm text-gray-700 dark:text-gray-300">AI thinking...</span>
        </div>
      )}

      {error && (
        <div className="p-2 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 text-sm rounded-lg mb-4">
          {error}
        </div>
      )}

      {/* Game Board */}
      <div className="grid grid-cols-3 gap-3 max-w-xs mx-auto mb-4">
        {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((index) => {
          const symbol = getCellSymbol(index);
          const isAvailable = isCellAvailable(index);

          return (
            <button
              key={index}
              onClick={() => makeMove(index)}
              disabled={!isAvailable || aiThinking}
              className={`
                aspect-square rounded-lg text-4xl font-bold
                transition-all duration-200 transform
                flex items-center justify-center
                ${symbol === 'X' ? 'text-blue-400 dark:text-blue-300' : ''}
                ${symbol === 'O' ? 'text-red-500 dark:text-red-400' : ''}
                ${isAvailable && !aiThinking
                  ? 'bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#252525] dark:hover:bg-[#252525] hover:scale-105 cursor-pointer shadow-lg active:scale-95'
                  : 'bg-[#0f0f0f] dark:bg-[#0f0f0f] cursor-not-allowed opacity-60'
                }
              `}
            >
              {symbol}
            </button>
          );
        })}
      </div>

      {/* AI Reasoning */}
      {gameState.ai_reasoning && (
        <div className="mt-4 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
          <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
            🤖 AI's Move:
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">
            {gameState.ai_reasoning}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-4 text-center text-xs text-gray-500 dark:text-gray-400">
        Click any empty cell to make your move
      </div>
    </div>
  );
}
