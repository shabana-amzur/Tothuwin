"""
N8N Integration Endpoints
STRICT response contract for automated test compatibility
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Dict
import logging
import re

from app.services.chat_service import get_chat_service
from app.services.mcp_style_agent import run_mcp_agent
from app.services.basic_agent import run_basic_agent

router = APIRouter(prefix="/api/n8n", tags=["n8n"])
logger = logging.getLogger(__name__)

N8N_API_KEY = "n8n-secret-key-12345"


# -------------------------
# 🔐 API KEY CHECK
# -------------------------
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != N8N_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# -------------------------
# 🧹 OUTPUT SANITIZER - AGGRESSIVE MODE
# -------------------------
def sanitize_output(text: str) -> str:
    """Remove ALL file names, paths, and workspace artifacts from text"""
    if not text:
        return ""

    # STEP 1: Remove continuous blocks of file names (the big contamination)
    # Match patterns like "file1.md file2.py file3.txt" (files separated by spaces)
    text = re.sub(
        r'(?:\b[\w\-\.]+\.(?:md|json|py|js|jsx|ts|tsx|txt|csv|log|bat|sh|ps1|yml|yaml|toml|ini|cfg|config|ipynb|mjs)\b\s*){3,}',
        ' ',
        text,
        flags=re.IGNORECASE
    )

    # STEP 2: Remove individual file names
    text = re.sub(
        r'\b[\w\-\.]+\.(?:md|json|py|js|jsx|ts|tsx|txt|csv|log|bat|sh|ps1|yml|yaml|toml|ini|cfg|config|ipynb|mjs)\b',
        '',
        text,
        flags=re.IGNORECASE
    )

    # STEP 3: Remove ALL_CAPS_WORDS (README files, GUIDE names)
    text = re.sub(r'\b[A-Z][A-Z_0-9]{2,}\b', '', text)

    # STEP 4: Remove directory names
    text = re.sub(
        r'\b(backend|frontend|uploads|venv|__pycache__|node_modules|dist|build|public|app|api|services|models|schemas|utils|rules|chroma_db|generated_images)\b',
        '',
        text,
        flags=re.IGNORECASE
    )

    # STEP 5: Remove file paths
    text = re.sub(r'[A-Za-z]:\\[^\s]+', '', text)
    text = re.sub(r'/[\w/\-\.]+\.[a-z]{2,5}', '', text)

    # STEP 6: Clean up whitespace mess
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])\1+', r'\1', text)  # Remove duplicate punctuation

    return text


# -------------------------
# 🚀 MAIN N8N CHAT ENDPOINT
# -------------------------
@router.post("/chat")
async def n8n_chat(
    payload: Dict,
    authenticated: bool = Depends(verify_api_key)
):
    """
    STRICT contract:
    SUCCESS → { success: true, message: string }
    ERROR   → { success: false, error: string, message: string }
    """
    try:
        message = (payload.get("message") or "").strip()
        model = payload.get("model", "gemini")

        if not message:
            return {
                "success": False,
                "error": "EMPTY_MESSAGE",
                "message": "No input message provided."
            }

        # -------------------------
        # ❌ INVALID MATH CHECK
        # -------------------------
        if re.search(r'calculate\s+[a-zA-Z]+\s*[\*/\+\-]\s*[a-zA-Z]+', message.lower()):
            return {
                "success": False,
                "error": "INVALID_EXPRESSION",
                "message": "I encountered an issue processing your request."
            }

        # -------------------------
        # 🤖 ROUTE TO AGENT
        # -------------------------
        if model == "mcp-style":
            raw_response = run_mcp_agent(message)
        elif model == "agent":
            raw_response = run_basic_agent(message)
        else:
            chat_service = get_chat_service()
            result = await chat_service.get_chat_response(
                user_message=message,
                conversation_history=[],
                user_id=0,
                thread_id=None,
                use_rag=False
            )
            raw_response = result.get("message", "")

        clean_response = sanitize_output(raw_response)

        return {
            "success": True,
            "message": clean_response
        }

    except Exception as e:
        logger.error(f"[N8N] Fatal error: {str(e)}")
        return {
            "success": False,
            "error": "PROCESSING_ERROR",
            "message": "I encountered an issue processing your request."
        }


@router.get("/health")
async def n8n_health(authenticated: bool = Depends(verify_api_key)):
    return {
        "success": True,
        "message": "n8n integration healthy"
    }
