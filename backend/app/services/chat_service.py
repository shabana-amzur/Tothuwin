"""
Chat Service - LangChain + Google Gemini Integration
Handles all AI chat logic using LangChain
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict
from datetime import datetime
import logging

from ..config import get_settings
from .image_service import get_image_service
from .web_search_service import get_web_search_service

logger = logging.getLogger(__name__)
settings = get_settings()


class ChatService:
    """
    Service for handling chat interactions with Google Gemini via LangChain
    """
    
    def __init__(self):
        """Initialize the chat service with Gemini model"""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_GEMINI_API_KEY,
            temperature=settings.GEMINI_TEMPERATURE,
            max_output_tokens=settings.GEMINI_MAX_TOKENS,
        )
        logger.info(f"ChatService initialized with model: {settings.GEMINI_MODEL}")
    
    def _format_conversation_history(
        self, 
        history: List[Dict[str, str]]
    ) -> List:
        """
        Convert conversation history to LangChain message format
        
        Args:
            history: List of message dictionaries with 'role' and 'content'
        
        Returns:
            List of LangChain message objects
        """
        messages = []
        
        for msg in history:
            role = msg.get("role", "").lower()
            content = msg.get("content", "")
            
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
            elif role == "system":
                messages.append(SystemMessage(content=content))
        
        return messages
    
    def _needs_web_search(self, user_message: str) -> bool:
        """
        Detect if the user's query requires real-time web information
        
        Args:
            user_message: The user's input message
            
        Returns:
            True if web search is needed
        """
        search_keywords = [
            # News related
            'breaking news', 'latest news', 'current news', 'today news',
            'recent news', 'news about', 'what happened', 'headlines',
            
            # Time-sensitive phrases
            'current', 'latest', 'recent', 'today', 'now', 'this week',
            'this month', 'this year', 'right now', 'at the moment',
            
            # Events and happenings
            'events', 'happening', 'going on', 'taking place', 'scheduled',
            'upcoming', 'public events',
            
            # Real-time data
            'weather', 'temperature', 'forecast',
            'stock price', 'share price', 'market price', 'trading',
            'price today', 'price now', 'cost today',
            'live', 'real-time', 'live score', 'match score',
            
            # Sports and entertainment
            'score', 'match', 'game result', 'tournament', 'championship',
            
            # General current info
            'what are', 'what is happening', 'status of', 'update on'
        ]
        
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in search_keywords)
    
    async def get_chat_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        user_id: int = None,
        thread_id: int = None,
        use_rag: bool = False
    ) -> Dict[str, str]:
        """
        Get response from Gemini for the user's message
        
        Args:
            user_message: The user's input message
            conversation_history: Optional list of previous messages
            user_id: User ID for RAG
            thread_id: Thread ID for thread-specific RAG
            use_rag: Whether to use RAG with user's documents
        
        Returns:
            Dictionary with response message and metadata
        """
        try:
            # Check if this is an image generation request
            image_service = get_image_service()
            if image_service.detect_image_request(user_message):
                logger.info("Image generation request detected")
                result = await image_service.generate_image(user_message, user_id)
                return result
            
            # Check if web search is needed for real-time information
            web_search_context = ""
            used_web_search = False
            if self._needs_web_search(user_message):
                logger.info("Real-time information request detected, performing web search")
                web_search_service = get_web_search_service()
                
                # Determine if it's a news query
                if any(word in user_message.lower() for word in ['news', 'breaking', 'latest']):
                    search_results = web_search_service.get_news(user_message, max_results=5)
                else:
                    search_results = web_search_service.search(user_message, max_results=5)
                
                if search_results:
                    web_search_context = web_search_service.format_search_results(search_results)
                    used_web_search = True
                    logger.info(f"Found {len(search_results)} web results")
            
            # Build message list
            messages = []
            
            # Check if should use RAG with thread-specific documents
            rag_context = ""
            documents_found = False
            if use_rag and user_id and thread_id:
                from app.services.rag_service import get_rag_service
                rag_service = get_rag_service()
                
                # Check if thread has documents
                if rag_service.should_use_rag(user_id, thread_id):
                    # Retrieve relevant chunks
                    chunks = rag_service.retrieve_relevant_chunks(user_id, thread_id, user_message)
                    if chunks:
                        rag_context = rag_service.format_context_for_prompt(chunks)
                        documents_found = True
                        logger.info(f"Using RAG with {len(chunks)} chunks for user {user_id} thread {thread_id}")
            
            # Add system message for context
            system_prompt = (
                "You are a helpful, friendly, and knowledgeable AI assistant. "
                "Provide clear, accurate, and concise responses. "
                "Format your responses using markdown when appropriate."
            )
            
            # If web search results are available, add them to the context
            if web_search_context:
                system_prompt += (
                    "\n\n**CURRENT WEB SEARCH RESULTS:**\n" + 
                    web_search_context +
                    "\n\nIMPORTANT: Use the above search results to provide up-to-date, accurate information. "
                    "Summarize the key points and cite sources when relevant."
                )
            
            # If RAG context is available, add it to system prompt with strict grounding instructions
            elif rag_context:
                system_prompt += (
                    "\n\n" + rag_context + 
                    "\n\nIMPORTANT INSTRUCTIONS:\n"
                    "1. Answer ONLY based on the information provided in the documents above.\n"
                    "2. If the question cannot be answered using the document content, respond with: "
                    "\"I cannot find this information in the uploaded document.\"\n"
                    "3. Do not use external knowledge or make assumptions beyond what's in the documents.\n"
                    "4. Cite the document name when providing information."
                )
            
            messages.append(SystemMessage(content=system_prompt))
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(
                    self._format_conversation_history(conversation_history)
                )
            
            # Add current user message
            messages.append(HumanMessage(content=user_message))
            
            # Get response from Gemini
            logger.info(f"Sending request to Gemini with {len(messages)} messages (RAG: {documents_found})")
            response = await self.llm.ainvoke(messages)
            
            logger.info("Successfully received response from Gemini")
            
            return {
                "message": response.content,
                "model": settings.GEMINI_MODEL,
                "timestamp": datetime.now().isoformat(),
                "used_rag": documents_found,
                "used_web_search": used_web_search
            }
            
        except Exception as e:
            logger.error(f"Error in get_chat_response: {str(e)}")
            raise Exception(f"Failed to get chat response: {str(e)}")
    
    async def get_chat_response_with_image(
        self,
        user_message: str,
        image_base64: str,
        mime_type: str = "image/jpeg",
        user_id: int = None,
        thread_id: int = None,
        db = None
    ) -> Dict[str, str]:
        """
        Get response from Gemini Vision for image analysis
        
        Args:
            user_message: The user's question about the image
            image_base64: Base64 encoded image data
            mime_type: MIME type of the image
            user_id: User ID for saving to database
            thread_id: Thread ID for conversation context
            db: Database session
        
        Returns:
            Dictionary with response message and metadata
        """
        try:
            from langchain_core.messages import HumanMessage
            
            # Create a message with both text and image
            message_content = [
                {
                    "type": "text",
                    "text": user_message or "What's in this image? Provide detailed information including any text, objects, or medical information visible."
                },
                {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{image_base64}"
                }
            ]
            
            message = HumanMessage(content=message_content)
            
            logger.info(f"Sending image analysis request to Gemini Vision")
            response = await self.llm.ainvoke([message])
            
            logger.info("Successfully received image analysis from Gemini")
            
            # Save to database if db session provided
            if db and user_id:
                from app.models.database import ChatHistory, ChatThread
                from datetime import datetime
                
                # Create or get thread
                if not thread_id:
                    new_thread = ChatThread(
                        user_id=user_id,
                        title="Image Analysis",
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.add(new_thread)
                    db.commit()
                    db.refresh(new_thread)
                    thread_id = new_thread.id
                
                # Save chat history
                chat_entry = ChatHistory(
                    user_id=user_id,
                    thread_id=thread_id,
                    message=f"🖼️ {user_message}",
                    response=response.content,
                    model=settings.GEMINI_MODEL,
                    created_at=datetime.now()
                )
                db.add(chat_entry)
                db.commit()
                
                logger.info(f"Saved image chat to database for user {user_id}, thread {thread_id}")
            
            return {
                "message": response.content,
                "model": settings.GEMINI_MODEL + " (Vision)",
                "timestamp": datetime.now().isoformat(),
                "thread_id": thread_id
            }
            
        except Exception as e:
            logger.error(f"Error in get_chat_response_with_image: {str(e)}")
            raise Exception(f"Failed to analyze image: {str(e)}")
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model"""
        return {
            "model": settings.GEMINI_MODEL,
            "temperature": str(settings.GEMINI_TEMPERATURE),
            "max_tokens": str(settings.GEMINI_MAX_TOKENS)
        }


# Singleton instance
_chat_service_instance = None


def get_chat_service() -> ChatService:
    """Get or create ChatService singleton instance"""
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService()
    return _chat_service_instance
