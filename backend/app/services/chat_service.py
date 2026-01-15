"""
Chat Service - LangChain + Google Gemini Integration
Handles all AI chat logic using LangChain
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict
from datetime import datetime
import logging

from ..config import get_settings

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
    
    async def get_chat_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        user_id: int = None,
        use_rag: bool = False
    ) -> Dict[str, str]:
        """
        Get response from Gemini for the user's message
        
        Args:
            user_message: The user's input message
            conversation_history: Optional list of previous messages
            user_id: User ID for RAG
            use_rag: Whether to use RAG with user's documents
        
        Returns:
            Dictionary with response message and metadata
        """
        try:
            # Build message list
            messages = []
            
            # Check if should use RAG
            rag_context = ""
            if use_rag and user_id:
                from app.services.rag_service import get_rag_service
                rag_service = get_rag_service()
                
                # Retrieve relevant chunks
                chunks = rag_service.retrieve_relevant_chunks(user_id, user_message)
                if chunks:
                    rag_context = rag_service.format_context_for_prompt(chunks)
                    logger.info(f"Using RAG with {len(chunks)} chunks for user {user_id}")
            
            # Add system message for context
            system_prompt = (
                "You are a helpful, friendly, and knowledgeable AI assistant. "
                "Provide clear, accurate, and concise responses. "
                "Format your responses using markdown when appropriate."
            )
            
            # If RAG context is available, add it to system prompt
            if rag_context:
                system_prompt += "\n\n" + rag_context + "\nPlease answer the user's question based on the above context."
            
            messages.append(SystemMessage(content=system_prompt))
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(
                    self._format_conversation_history(conversation_history)
                )
            
            # Add current user message
            messages.append(HumanMessage(content=user_message))
            
            # Get response from Gemini
            logger.info(f"Sending request to Gemini with {len(messages)} messages")
            response = await self.llm.ainvoke(messages)
            
            logger.info("Successfully received response from Gemini")
            
            return {
                "message": response.content,
                "model": settings.GEMINI_MODEL,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in get_chat_response: {str(e)}")
            raise Exception(f"Failed to get chat response: {str(e)}")
    
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
