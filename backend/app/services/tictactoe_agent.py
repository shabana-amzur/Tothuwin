"""
Tic-Tac-Toe game with AI using Langchain and Gemini
"""
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os


class TicTacToeGame:
    """Tic-Tac-Toe game state manager"""
    
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # 9 positions (0-8)
        self.current_player = 'X'  # Human is X, AI is O
        self.game_over = False
        self.winner = None
        
    def reset(self):
        """Reset the game"""
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        
    def get_board_string(self) -> str:
        """Get board as a formatted string"""
        return f"""
        {self.board[0]} | {self.board[1]} | {self.board[2]}
        ---------
        {self.board[3]} | {self.board[4]} | {self.board[5]}
        ---------
        {self.board[6]} | {self.board[7]} | {self.board[8]}
        """
    
    def get_available_moves(self) -> List[int]:
        """Get list of available positions"""
        return [i for i in range(9) if self.board[i] == ' ']
    
    def make_move(self, position: int, player: str) -> bool:
        """Make a move on the board"""
        if position < 0 or position > 8:
            return False
        if self.board[position] != ' ':
            return False
        
        self.board[position] = player
        return True
    
    def check_winner(self) -> Optional[str]:
        """Check if there's a winner"""
        # Winning combinations
        winning_combos = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for combo in winning_combos:
            if (self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] 
                and self.board[combo[0]] != ' '):
                return self.board[combo[0]]
        
        # Check for draw
        if ' ' not in self.board:
            return 'Draw'
        
        return None
    
    def update_game_state(self):
        """Update game over status"""
        result = self.check_winner()
        if result:
            self.game_over = True
            self.winner = result
    
    def find_winning_move(self, player: str) -> Optional[int]:
        """Find a position that would win for the given player"""
        winning_combos = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        
        for combo in winning_combos:
            values = [self.board[i] for i in combo]
            if values.count(player) == 2 and values.count(' ') == 1:
                for i in combo:
                    if self.board[i] == ' ':
                        return i
        return None


class TicTacToeAgent:
    """AI agent for playing Tic-Tac-Toe using strategic logic"""
    
    def __init__(self):
        self.game = TicTacToeGame()
        
        # Initialize Gemini model (optional - for future enhancements)
        api_key = os.getenv("GEMINI_API_KEY")
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=api_key,
                temperature=0.3
            )
        except:
            self.llm = None
    
    def reset_game(self):
        """Reset the game"""
        self.game.reset()
    
    def make_human_move(self, position: int) -> dict:
        """Human makes a move"""
        if self.game.game_over:
            return {
                "success": False,
                "message": "Game is over. Start a new game.",
                "board": self.game.board,
                "game_over": True,
                "winner": self.game.winner
            }
        
        if position < 0 or position > 8:
            return {
                "success": False,
                "message": "Invalid position. Must be 0-8.",
                "board": self.game.board,
                "game_over": False
            }
        
        if self.game.board[position] != ' ':
            return {
                "success": False,
                "message": "Position already taken.",
                "board": self.game.board,
                "game_over": False
            }
        
        # Make human move
        self.game.make_move(position, 'X')
        self.game.update_game_state()
        
        if self.game.game_over:
            return {
                "success": True,
                "message": "Move made",
                "board": self.game.board,
                "game_over": True,
                "winner": self.game.winner
            }
        
        return {
            "success": True,
            "message": "Move made. AI's turn.",
            "board": self.game.board,
            "game_over": False
        }
    
    def make_ai_move(self) -> dict:
        """AI makes a move using strategic logic"""
        if self.game.game_over:
            return {
                "success": False,
                "message": "Game is over.",
                "board": self.game.board,
                "game_over": True,
                "winner": self.game.winner,
                "ai_position": None
            }
        
        # Strategy: Try to win, then block, then strategic positioning
        ai_position = None
        reasoning = ""
        
        # 1. Check if AI can win
        winning_move = self.game.find_winning_move('O')
        if winning_move is not None:
            ai_position = winning_move
            reasoning = f"I found a winning move at position {ai_position}! Taking it to win the game."
        
        # 2. Check if need to block human
        elif (blocking_move := self.game.find_winning_move('X')) is not None:
            ai_position = blocking_move
            reasoning = f"I need to block your winning move at position {ai_position}."
        
        # 3. Use strategic positioning
        else:
            available = self.game.get_available_moves()
            
            # Strategic preferences
            center = 4
            corners = [0, 2, 6, 8]
            
            # Prefer center if available
            if center in available:
                ai_position = center
                reasoning = "Taking the center position (4) for strategic advantage."
            # Prefer corners
            elif any(c in available for c in corners):
                corner_available = [c for c in corners if c in available]
                ai_position = corner_available[0]
                reasoning = f"Taking corner position {ai_position} for strategic positioning."
            # Take any available
            else:
                ai_position = available[0]
                reasoning = f"Taking available position {ai_position}."
        
        if ai_position is None:
            return {
                "success": False,
                "message": "No moves available",
                "board": self.game.board,
                "game_over": False,
                "ai_position": None
            }
        
        # Make the move
        self.game.make_move(ai_position, 'O')
        self.game.update_game_state()
        
        return {
            "success": True,
            "message": "AI made a move",
            "board": self.game.board,
            "game_over": self.game.game_over,
            "winner": self.game.winner if self.game.game_over else None,
            "ai_position": ai_position,
            "ai_reasoning": reasoning
        }
    
    def get_game_state(self) -> dict:
        """Get current game state"""
        return {
            "board": self.game.board,
            "game_over": self.game.game_over,
            "winner": self.game.winner,
            "available_moves": self.game.get_available_moves(),
            "current_player": self.game.current_player
        }
