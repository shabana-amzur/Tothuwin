"""
N8N Agent Integration API
Handles communication between the chat app and N8N workflows
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
from app.models.database import User
from app.utils.auth import get_current_active_user
import os

router = APIRouter()

N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")


class N8NWorkflowRequest(BaseModel):
    workflow_id: str
    data: Dict[str, Any]


class N8NWebhookRequest(BaseModel):
    webhook_id: str
    data: Dict[str, Any]


class N8NAgentRequest(BaseModel):
    agent_type: str
    prompt: str
    context: Optional[Dict[str, Any]] = None


@router.post("/workflow/execute")
async def execute_n8n_workflow(
    request: N8NWorkflowRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Execute an N8N workflow"""
    try:
        async with httpx.AsyncClient() as client:
            headers = {}
            if N8N_API_KEY:
                headers["X-N8N-API-KEY"] = N8N_API_KEY
            
            response = await client.post(
                f"{N8N_URL}/api/v1/workflows/{request.workflow_id}/execute",
                json=request.data,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"N8N workflow execution failed: {response.text}"
                )
            
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to N8N: {str(e)}"
        )


@router.post("/webhook/trigger")
async def trigger_n8n_webhook(
    request: N8NWebhookRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Trigger an N8N webhook"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_URL}/webhook/{request.webhook_id}",
                json=request.data,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"N8N webhook trigger failed: {response.text}"
                )
            
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to N8N: {str(e)}"
        )


@router.post("/agent/execute")
async def execute_n8n_agent(
    request: N8NAgentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute an N8N AI agent workflow
    Supports different agent types: research, task_automation, data_analysis
    """
    try:
        # Prepare data for N8N agent workflow
        agent_data = {
            "user_id": current_user.id,
            "user_email": current_user.email,
            "agent_type": request.agent_type,
            "prompt": request.prompt,
            "context": request.context or {},
            "timestamp": str(current_user.created_at)
        }
        
        # Trigger the agent webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_URL}/webhook/ai-agent",
                json=agent_data,
                timeout=60.0  # Agents may take longer
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"N8N agent execution failed: {response.text}"
                )
            
            result = response.json()
            
            return {
                "success": True,
                "agent_type": request.agent_type,
                "result": result,
                "message": f"Agent '{request.agent_type}' executed successfully"
            }
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to N8N agent: {str(e)}"
        )


@router.post("/webhook/receive")
async def receive_n8n_webhook(request: Request):
    """
    Receive webhooks from N8N workflows
    This endpoint allows N8N to send data back to the application
    """
    try:
        data = await request.json()
        
        # Process the webhook data
        # You can add custom logic here to handle different webhook types
        
        return {
            "success": True,
            "message": "Webhook received successfully",
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process webhook: {str(e)}"
        )


@router.get("/workflows/list")
async def list_n8n_workflows(
    current_user: User = Depends(get_current_active_user)
):
    """List all available N8N workflows"""
    try:
        async with httpx.AsyncClient() as client:
            headers = {}
            if N8N_API_KEY:
                headers["X-N8N-API-KEY"] = N8N_API_KEY
            
            response = await client.get(
                f"{N8N_URL}/api/v1/workflows",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch N8N workflows"
                )
            
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to N8N: {str(e)}"
        )


@router.get("/health")
async def check_n8n_health():
    """Check if N8N is running and accessible"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{N8N_URL}/healthz",
                timeout=5.0
            )
            
            return {
                "n8n_status": "healthy" if response.status_code == 200 else "unhealthy",
                "n8n_url": N8N_URL,
                "status_code": response.status_code
            }
    except httpx.RequestError as e:
        return {
            "n8n_status": "unreachable",
            "n8n_url": N8N_URL,
            "error": str(e)
        }
