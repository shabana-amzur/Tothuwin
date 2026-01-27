# Tic-Tac-Toe with Langchain Agent

## Overview
An intelligent Tic-Tac-Toe game where you play against a Langchain-powered AI agent that uses strategic reasoning to make optimal moves.

## Features

### 🤖 Langchain Agent
- **ReAct Agent Pattern**: The AI uses the Thought-Action-Observation loop to analyze the game
- **Strategic Tools**: 
  - `get_board`: Retrieves current board state and available moves
  - `analyze_board`: Analyzes for winning moves, blocking moves, and strategic positions
  - `make_move`: Executes the AI's chosen move

### 🎮 Game Features
- **Real-time Gameplay**: Instant AI responses after your move
- **Strategic AI**: The AI follows a priority strategy:
  1. Win in one move (if possible)
  2. Block opponent's winning move
  3. Take center position
  4. Take corner positions
  5. Take any available position
- **Game State Management**: Persistent game sessions per user
- **Visual Feedback**: 
  - Clear board visualization with X and O symbols
  - Available moves highlighted
  - Game status messages
  - Winner announcements
- **AI Reasoning Display**: View the AI's thought process (optional)

## API Endpoints

### Start New Game
```http
POST /api/tictactoe/new
Authorization: Bearer {token}
```
Starts a new game. You play as X, AI plays as O.

**Response:**
```json
{
  "board": [" ", " ", " ", " ", " ", " ", " ", " ", " "],
  "game_over": false,
  "winner": null,
  "available_moves": [0, 1, 2, 3, 4, 5, 6, 7, 8],
  "message": "New game started! You are X, AI is O. Make your move!"
}
```

### Make Move
```http
POST /api/tictactoe/move
Authorization: Bearer {token}
Content-Type: application/json

{
  "position": 4
}
```
Make your move (0-8) and AI will automatically respond.

**Response:**
```json
{
  "board": ["X", " ", " ", " ", "O", " ", " ", " ", " "],
  "game_over": false,
  "winner": null,
  "available_moves": [1, 2, 3, 5, 6, 7, 8],
  "message": "AI made a move",
  "ai_position": 4,
  "ai_reasoning": "Thought: I should take the center position as it's the strongest strategic position..."
}
```

### Get Game State
```http
GET /api/tictactoe/state
Authorization: Bearer {token}
```
Retrieve current game state without making a move.

### Reset Game
```http
POST /api/tictactoe/reset
Authorization: Bearer {token}
```
Reset the current game to start fresh.

## Board Positions

The board uses positions 0-8:
```
0 | 1 | 2
---------
3 | 4 | 5
---------
6 | 7 | 8
```

## Frontend Usage

Navigate to `/tictactoe` to play the game. The interface provides:

1. **Interactive Board**: Click any available cell to make your move
2. **Status Updates**: Real-time game status and messages
3. **AI Thinking Indicator**: Shows when AI is processing
4. **Winner Announcement**: Clear display when game ends
5. **New Game Button**: Start a fresh game anytime
6. **AI Reasoning**: Expandable section to view AI's thought process

## Technical Implementation

### Backend (Python)
- **FastAPI**: REST API endpoints
- **Langchain**: Agent framework for AI decision making
- **Google Gemini**: LLM for strategic reasoning
- **Pydantic Tools**: Type-safe tool definitions

### Frontend (Next.js)
- **React**: Component-based UI
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Modern styling
- **State Management**: React hooks for game state

### AI Strategy
The Langchain agent uses three tools to make decisions:

1. **Get Board Tool**: Retrieves current board state
2. **Analyze Board Tool**: 
   - Detects winning moves for AI
   - Identifies blocking moves needed
   - Suggests strategic positions (center, corners)
3. **Make Move Tool**: Executes the chosen position

The agent follows the ReAct pattern:
```
Thought → Action → Observation → Thought → ... → Final Answer
```

## Game Logic

### Win Conditions
- 3 in a row horizontally
- 3 in a row vertically
- 3 in a row diagonally

### Draw Condition
- All positions filled with no winner

### Move Validation
- Position must be 0-8
- Position must be empty
- Game must not be over

## Example Game Flow

1. **User clicks position 0** (top-left)
   - Board: `X _ _  _ _ _  _ _ _`
   - AI analyzes and takes center (position 4)
   - Board: `X _ _  _ O _  _ _ _`

2. **User clicks position 2** (top-right)
   - Board: `X _ X  _ O _  _ _ _`
   - AI blocks by taking position 1
   - Board: `X O X  _ O _  _ _ _`

3. **User clicks position 6** (bottom-left)
   - Board: `X O X  _ O _  X _ _`
   - AI blocks by taking position 3
   - Board: `X O X  O O _  X _ _`

4. **User clicks position 5** (middle-right)
   - Board: `X O X  O O X  X _ _`
   - AI takes position 7 to block potential win
   - Board: `X O X  O O X  X O _`

5. **User clicks position 8** (bottom-right)
   - Board: `X O X  O O X  X O X`
   - **Draw!** All positions filled

## Testing

Test the game with these scenarios:

1. **AI Winning Move**: Let AI get two in a row, it will complete the win
2. **Blocking**: Try to get two in a row, AI will block
3. **Center Control**: AI prioritizes center position early
4. **Corner Strategy**: If center is taken, AI prefers corners
5. **Draw Scenario**: Play optimally to reach a draw

## Dependencies

**Backend:**
```
langchain
langchain-google-genai
google-generativeai
fastapi
pydantic
```

**Frontend:**
```
next
react
typescript
tailwindcss
```

## Environment Variables

Required in `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

## Access

- **Frontend**: http://localhost:3000/tictactoe
- **API Docs**: http://localhost:8001/docs (see Tic-Tac-Toe section)

## Future Enhancements

Potential improvements:
- [ ] Difficulty levels (easy, medium, hard)
- [ ] Minimax algorithm comparison
- [ ] Game statistics tracking
- [ ] Multiplayer mode
- [ ] Winning line animation
- [ ] Move history replay
- [ ] Save/load games
- [ ] Leaderboard

## Conclusion

This implementation demonstrates:
- Langchain agent patterns for game AI
- Tool-based reasoning with LLMs
- Strategic decision making
- Real-time interactive gameplay
- Clean separation of game logic and AI

Enjoy playing against the AI! 🎮
