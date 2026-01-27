"""
Tic-Tac-Toe API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.services.tictactoe_agent import TicTacToeAgent
from app.models.database import User
from app.utils.auth import get_current_active_user

router = APIRouter()

# Store game sessions (in production, use Redis or database)
game_sessions = {}


class MoveRequest(BaseModel):
    position: int


class GameResponse(BaseModel):
    board: List[str]
    game_over: bool
    winner: Optional[str]
    available_moves: List[int]
    message: str
    ai_position: Optional[int] = None
    ai_reasoning: Optional[str] = None


@router.post("/new", response_model=GameResponse)
async def new_game(current_user: User = Depends(get_current_active_user)):
    """Start a new tic-tac-toe game"""
    user_id = current_user.id
    
    # Create new game instance
    agent = TicTacToeAgent()
    game_sessions[user_id] = agent
    
    state = agent.get_game_state()
    
    return GameResponse(
        board=state["board"],
        game_over=state["game_over"],
        winner=state["winner"],
        available_moves=state["available_moves"],
        message="New game started! You are X, AI is O. Make your move!"
    )


@router.post("/move", response_model=GameResponse)
async def make_move(
    move: MoveRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Make a move in the tic-tac-toe game"""
    user_id = current_user.id
    
    # Get or create game session
    if user_id not in game_sessions:
        agent = TicTacToeAgent()
        game_sessions[user_id] = agent
    else:
        agent = game_sessions[user_id]
    
    # Make human move
    human_result = agent.make_human_move(move.position)
    
    if not human_result["success"]:
        return GameResponse(
            board=human_result["board"],
            game_over=human_result.get("game_over", False),
            winner=human_result.get("winner"),
            available_moves=agent.get_game_state()["available_moves"],
            message=human_result["message"]
        )
    
    # Check if game ended after human move
    if human_result["game_over"]:
        return GameResponse(
            board=human_result["board"],
            game_over=True,
            winner=human_result["winner"],
            available_moves=[],
            message=f"Game over! Winner: {human_result['winner']}"
        )
    
    # Make AI move
    ai_result = agent.make_ai_move()
    
    return GameResponse(
        board=ai_result["board"],
        game_over=ai_result["game_over"],
        winner=ai_result.get("winner"),
        available_moves=agent.get_game_state()["available_moves"],
        message=ai_result["message"],
        ai_position=ai_result.get("ai_position"),
        ai_reasoning=ai_result.get("ai_reasoning")
    )


@router.get("/state", response_model=GameResponse)
async def get_game_state(current_user: User = Depends(get_current_active_user)):
    """Get current game state"""
    user_id = current_user.id
    
    if user_id not in game_sessions:
        raise HTTPException(status_code=404, detail="No active game. Start a new game first.")
    
    agent = game_sessions[user_id]
    state = agent.get_game_state()
    
    return GameResponse(
        board=state["board"],
        game_over=state["game_over"],
        winner=state["winner"],
        available_moves=state["available_moves"],
        message="Current game state"
    )


@router.post("/reset", response_model=GameResponse)
async def reset_game(current_user: User = Depends(get_current_active_user)):
    """Reset the current game"""
    user_id = current_user.id
    
    if user_id not in game_sessions:
        agent = TicTacToeAgent()
        game_sessions[user_id] = agent
    else:
        agent = game_sessions[user_id]
        agent.reset_game()
    
    state = agent.get_game_state()
    
    return GameResponse(
        board=state["board"],
        game_over=state["game_over"],
        winner=state["winner"],
        available_moves=state["available_moves"],
        message="Game reset! You are X, AI is O. Make your move!"
    )
