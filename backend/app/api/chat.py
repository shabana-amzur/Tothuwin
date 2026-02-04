"""
Chat API Routes
Handles all chat-related endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import logging

from ..models.chat import ChatRequest, ChatResponse, ErrorResponse
from ..services.chat_service import get_chat_service
from ..services.basic_agent import run_basic_agent
from ..services.mcp_style_agent import run_mcp_agent
from ..database import get_db
from ..models.database import User, ChatHistory, ChatThread
from ..utils.auth import get_current_active_user
from ..api.threads import generate_thread_title

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        500: {"model": ErrorResponse},
        400: {"model": ErrorResponse}
    },
    summary="Send a chat message",
    description="Send a message to the AI assistant and receive a response"
)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Chat endpoint - sends user message to Gemini and returns AI response
    Requires authentication and saves chat history to database
    
    **Request Body:**
    - message: User's message (required)
    - conversation_history: List of previous messages (optional)
    - thread_id: Thread ID to associate message with (optional)
    
    **Returns:**
    - AI assistant's response with timestamp and model info
    """
    try:
        logger.info(f"User {current_user.email} sent message with length: {len(request.message)}")
        
        # Handle thread creation or retrieval
        thread_id = request.thread_id
        is_new_thread = False
        
        if thread_id is None:
            # Create a new thread
            new_thread = ChatThread(user_id=current_user.id, title="New Conversation")
            db.add(new_thread)
            db.commit()
            db.refresh(new_thread)
            thread_id = new_thread.id
            is_new_thread = True
            logger.info(f"Created new thread {thread_id} for user {current_user.email}")
        else:
            # Verify thread belongs to user
            thread = db.query(ChatThread).filter(
                ChatThread.id == thread_id,
                ChatThread.user_id == current_user.id
            ).first()
            if not thread:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Thread not found"
                )
        
        # Get last 5 conversation pairs from this thread for conversation memory
        # Each ChatHistory record contains one user message and one AI response
        recent_messages = db.query(ChatHistory).filter(
            ChatHistory.thread_id == thread_id
        ).order_by(ChatHistory.created_at.desc()).limit(5).all()
        
        # Build conversation history (reverse to chronological order)
        # This will include up to 5 previous user messages and 5 previous AI responses
        history = []
        for msg in reversed(recent_messages):
            history.append({"role": "user", "content": msg.message})
            history.append({"role": "assistant", "content": msg.response})
        
        logger.info(f"Retrieved {len(recent_messages)} previous conversation pairs for thread {thread_id}")
        
        # Route to appropriate model based on request
        selected_model = request.model or "gemini"
        logger.info(f"🎯 Using model: {selected_model} for user {current_user.email}")
        
        if selected_model == "n8n":
            # Route to N8N multi-agent workflow
            import httpx
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "http://localhost:5678/webhook/multi-agent",
                        json={"message": request.message}
                    )
                    response.raise_for_status()
                    n8n_result = response.json()
                    
                    result = {
                        "message": n8n_result.get("message", ""),
                        "model": "N8N Multi-Agent"
                    }
            except Exception as e:
                logger.error(f"N8N workflow error: {str(e)}")
                result = {
                    "message": f"N8N Multi-Agent workflow encountered an error: {str(e)}\\n\\nPlease ensure n8n is running and try again.",
                    "model": "N8N Multi-Agent (Error)"
                }
        elif selected_model == "mcp-style":
            # Use MCP Style Agent (Planner-Selector-Executor-Synthesizer)
            logger.info(f"🤖 Using MCP STYLE AGENT for user {current_user.email}")
            try:
                mcp_response = run_mcp_agent(request.message)
                result = {
                    "message": mcp_response,
                    "model": "MCP Style Agent"
                }
            except Exception as e:
                logger.error(f"MCP Style Agent error: {str(e)}")
                result = {
                    "message": f"MCP Style Agent encountered an error: {str(e)}\\n\\nPlease try again or select a different model.",
                    "model": "MCP Style Agent (Error)"
                }
        elif selected_model == "rag":
            # Use RAG mode (document-grounded chat)
            logger.info(f"📚 Using RAG CHAT for user {current_user.email}")
            chat_service = get_chat_service()
            
            # Force RAG mode - always use documents if available
            from app.services.rag_service import get_rag_service
            rag_service = get_rag_service()
            
            # Check if thread has documents
            if not rag_service.should_use_rag(current_user.id, thread_id):
                result = {
                    "message": "⚠️ **No documents uploaded yet!**\n\nTo use RAG Chat:\n1. Click the 📎 paperclip icon\n2. Upload a PDF, TXT, or DOCX file\n3. Ask questions about your document\n\nExample questions:\n- \"What is the main topic of this document?\"\n- \"Summarize the key points\"\n- \"Find information about [specific topic]\"",
                    "model": "RAG Chat"
                }
            else:
                result = await chat_service.get_chat_response(
                    user_message=request.message,
                    conversation_history=history,
                    user_id=current_user.id,
                    thread_id=thread_id,
                    use_rag=True  # Force RAG mode
                )
                result["model"] = "RAG Chat"
        elif selected_model == "agent" or request.use_agent:
            # Use Basic Agent (ReAct pattern with tools)
            logger.info(f"🤖 Using BASIC AGENT for user {current_user.email}")
            agent_response = run_basic_agent(request.message)
            result = {
                "message": agent_response,
                "model": "Gemini Agent"
            }
        else:
            # Use regular Gemini model (no automatic RAG)
            logger.info(f"💬 Using GEMINI for user {current_user.email}")
            chat_service = get_chat_service()
            
            result = await chat_service.get_chat_response(
                user_message=request.message,
                conversation_history=history,
                user_id=current_user.id,
                thread_id=thread_id,
                use_rag=False  # Gemini mode doesn't use RAG automatically
            )
        
        # Save chat history to database with thread_id
        try:
            chat_record = ChatHistory(
                user_id=current_user.id,
                thread_id=thread_id,
                message=request.message,
                response=result["message"],
                model=result.get("model", "gemini-2.5-flash"),
                session_id=request.session_id
            )
            db.add(chat_record)
            db.commit()
            logger.info(f"Chat history saved for user {current_user.email} in thread {thread_id}")
        except Exception as db_error:
            logger.error(f"Failed to save chat history: {str(db_error)}")
            db.rollback()
            # Continue even if saving fails
        
        # Auto-generate/update thread title based on latest conversation
        try:
            # Generate title from the current conversation context
            title = await generate_thread_title(request.message)
            db.query(ChatThread).filter(ChatThread.id == thread_id).update({"title": title})
            db.commit()
            logger.info(f"{'Generated' if is_new_thread else 'Updated'} title '{title}' for thread {thread_id}")
        except Exception as title_error:
            logger.error(f"Failed to generate thread title: {str(title_error)}")
        
        # Return response with optional image data
        response_data = {
            "message": result["message"],
            "model": result.get("model", "gemini-2.5-flash"),
            "thread_id": thread_id
        }
        
        # Include image data if present
        if result.get("is_image"):
            response_data["image_url"] = result.get("image_url")
            response_data["is_image"] = True
        
        return ChatResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )


@router.get(
    "/chat/model-info",
    summary="Get model information",
    description="Get information about the current AI model configuration"
)
async def get_model_info() -> Dict[str, str]:
    """Get information about the current Gemini model"""
    try:
        chat_service = get_chat_service()
        return chat_service.get_model_info()
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/agent/chat",
    summary="Simple agent endpoint for n8n",
    description="Lightweight endpoint that returns only the agent response (for n8n orchestration)"
)
async def agent_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Simplified chat endpoint for n8n integration.
    Returns only the agent response without UI logic.
    
    **Request Body:**
    - message: User's message (required)
    - thread_id: Thread ID (optional)
    - model: Model to use (optional, defaults to 'gemini')
    
    **Returns:**
    - response: Agent's text response
    - model: Model used
    - thread_id: Thread ID
    """
    try:
        logger.info(f"[N8N] User {current_user.email} sent message via n8n")
        
        # Handle thread
        thread_id = request.thread_id
        if thread_id is None:
            new_thread = ChatThread(user_id=current_user.id, title="N8N Conversation")
            db.add(new_thread)
            db.commit()
            db.refresh(new_thread)
            thread_id = new_thread.id
        
        # Get conversation history
        recent_messages = db.query(ChatHistory).filter(
            ChatHistory.thread_id == thread_id
        ).order_by(ChatHistory.created_at.desc()).limit(5).all()
        
        history = []
        for msg in reversed(recent_messages):
            history.append({"role": "user", "content": msg.message})
            history.append({"role": "assistant", "content": msg.response})
        
        # Route to appropriate agent
        selected_model = request.model or "gemini"
        
        if selected_model == "rag":
            # RAG mode for n8n endpoint
            from app.services.rag_service import get_rag_service
            rag_service = get_rag_service()
            
            if not rag_service.should_use_rag(current_user.id, thread_id):
                response_text = "No documents uploaded. Please upload documents to use RAG mode."
                model_used = "RAG Chat"
            else:
                chat_service = get_chat_service()
                result = await chat_service.get_chat_response(
                    user_message=request.message,
                    conversation_history=history,
                    user_id=current_user.id,
                    thread_id=thread_id,
                    use_rag=True
                )
                response_text = result["message"]
                model_used = "RAG Chat"
        elif selected_model == "mcp-style":
            mcp_response = run_mcp_agent(request.message)
            response_text = mcp_response
            model_used = "MCP Style Agent"
        elif selected_model == "agent" or request.use_agent:
            response_text = run_basic_agent(request.message)
            model_used = "Gemini Agent"
        else:
            chat_service = get_chat_service()
            from app.services.rag_service import get_rag_service
            rag_service = get_rag_service()
            use_rag = rag_service.should_use_rag(current_user.id, thread_id)
            
            result = await chat_service.get_chat_response(
                user_message=request.message,
                conversation_history=history,
                user_id=current_user.id,
                thread_id=thread_id,
                use_rag=use_rag
            )
            response_text = result["message"]
            model_used = result.get("model", "gemini-2.5-flash-lite")
        
        # Save to database
        chat_record = ChatHistory(
            user_id=current_user.id,
            thread_id=thread_id,
            message=request.message,
            response=response_text,
            model=model_used,
            session_id=request.session_id
        )
        db.add(chat_record)
        db.commit()
        
        logger.info(f"[N8N] Chat history saved for user {current_user.email} in thread {thread_id}")
        
        # Return simple response for n8n
        return {
            "response": response_text,
            "model": model_used,
            "thread_id": thread_id,
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"[N8N] Error in agent_chat: {str(e)}")
        # Return error as JSON (n8n can handle this)
        return {
            "response": "I encountered an error processing your request. Please try again.",
            "error": str(e),
            "model": "error",
            "thread_id": request.thread_id
        }


@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    session_id: str = None
):
    """Get chat history for the current user"""
    try:
        query = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id)
        
        if session_id:
            query = query.filter(ChatHistory.session_id == session_id)
        
        chat_history = query.order_by(ChatHistory.created_at.desc()).limit(limit).all()
        
        return {
            "history": [
                {
                    "id": chat.id,
                    "message": chat.message,
                    "response": chat.response,
                    "model": chat.model,
                    "session_id": chat.session_id,
                    "created_at": chat.created_at
                }
                for chat in chat_history
            ]
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )


@router.post(
    "/chat/image",
    summary="Chat with image",
    description="Send a message with an image for AI analysis"
)
async def chat_with_image(
    message: str = Form(...),
    image: UploadFile = Form(...),
    thread_id: Optional[int] = Form(None),
    model: str = Form("gemini"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Chat with image - analyze images and answer questions
    Works with Gemini, Agent, and MCP Style models (all use Gemini Vision API)
    """
    try:
        import base64
        from PIL import Image
        import io
        
        logger.info(f"Image chat request from user {current_user.email}: {message}")
        logger.info(f"Image: {image.filename}, Content-Type: {image.content_type}")
        logger.info(f"Selected model: {model}")
        
        # All models can now use Gemini Vision for image analysis
        # (Gemini, Agent, MCP Style all support images via Gemini Vision API)
        model_display_name = {
            "gemini": "Gemini Vision",
            "agent": "Agent (Gemini Vision)",
            "mcp-style": "MCP Style Agent (Gemini Vision)",
            "n8n": "N8N"
        }.get(model, "Gemini Vision")
        
        # N8N doesn't support vision yet
        if model == "n8n":
            return {
                "message": "⚠️ Image analysis is not available with N8N model. Please switch to 💬 Gemini, 🤖 Agent, or 🔧 MCP Style Agent to analyze images.",
                "thread_id": thread_id,
                "timestamp": None,
                "model": model
            }
        
        # Read and encode image
        image_data = await image.read()
        
        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Determine image MIME type
        mime_type = image.content_type or "image/jpeg"
        
        # Use chat service with vision
        chat_service = get_chat_service()
        result = await chat_service.get_chat_response_with_image(
            user_message=message,
            image_base64=image_base64,
            mime_type=mime_type,
            user_id=current_user.id,
            thread_id=thread_id,
            db=db
        )
        
        return {
            "message": result.get("message", ""),
            "thread_id": result.get("thread_id"),
            "timestamp": result.get("timestamp"),
            "model": model_display_name
        }
        
    except Exception as e:
        logger.error(f"Error in image chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        )
