"""
Agentic Content Generation API Endpoints

Provides RESTful endpoints for agentic content generation including:
- Starting/stopping content generation monitoring
- Generating content from natural language queries
- Getting agent status and monitoring information
- Managing knowledge card updates
"""

from fastapi import APIRouter, HTTPException, Body, Query
from typing import List, Dict, Any
from pydantic import BaseModel
import asyncio

from app.services.agentic_content import agentic_content_generator


router = APIRouter(
    prefix="/agentic",
    tags=["agentic"],
    responses={404: {"description": "Not found"}}
)


class ContentGenerationRequest(BaseModel):
    """Request model for content generation from queries"""
    query: str
    card_template_id: str = "KC-1"
    max_results: int = 5


class MonitoringStatus(BaseModel):
    """Response model for monitoring status"""
    monitoring_active: bool
    last_checked: str
    agents_status: Dict[str, Any]


@router.post("/generate/", response_model=Dict[str, Any])
async def generate_content(
    request: ContentGenerationRequest = Body(...)
):
    """
    Generate content based on a natural language query
    
    Args:
        request: ContentGenerationRequest containing query and parameters
        
    Returns:
        Dictionary with generated content and sources
    """
    try:
        result = await agentic_content_generator.generate_content_from_query(
            query=request.query,
            card_template_id=request.card_template_id
        )
        
        if result["success"]:
            return {
                "success": True,
                "content": result["content"],
                "sources": result["sources"],
                "message": "Content generated successfully"
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "message": "Content generation failed"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/start", response_model=Dict[str, Any])
async def start_monitoring():
    """
    Start the knowledge graph monitoring process
    
    Returns:
        Dictionary with monitoring status
    """
    try:
        # Start monitoring in background
        agentic_content_generator.monitoring_task = asyncio.create_task(
            agentic_content_generator.start_monitoring()
        )
        
        return {
            "success": True,
            "monitoring": "started",
            "message": "Knowledge graph monitoring started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/stop", response_model=Dict[str, Any])
async def stop_monitoring():
    """
    Stop the knowledge graph monitoring process
    
    Returns:
        Dictionary with monitoring status
    """
    try:
        if hasattr(agentic_content_generator, 'monitoring_task'):
            agentic_content_generator.monitoring_task.cancel()
            try:
                await agentic_content_generator.monitoring_task
            except asyncio.CancelledError:
                pass
            del agentic_content_generator.monitoring_task
        
        return {
            "success": True,
            "monitoring": "stopped",
            "message": "Knowledge graph monitoring stopped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/status", response_model=Dict[str, Any])
async def get_monitoring_status():
    """
    Get the current monitoring status
    
    Returns:
        Dictionary with monitoring status and agent information
    """
    try:
        status = agentic_content_generator.get_agent_status()
        
        return {
            "success": True,
            "monitoring_active": status.get("monitoring") == "active",
            "last_checked": status.get("last_checked"),
            "agents": status.get("agents", {}),
            "message": "Monitoring status retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/status", response_model=Dict[str, Any])
async def get_agent_status():
    """
    Get detailed status of all agents
    
    Returns:
        Dictionary with agent status information
    """
    try:
        status = agentic_content_generator.get_agent_status()
        
        return {
            "success": True,
            "agents": status.get("agents", {}),
            "message": "Agent status retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def agentic_health_check():
    """
    Health check endpoint for agentic content service
    
    Returns:
        Dictionary with health status
    """
    try:
        # Test agent initialization
        status = agentic_content_generator.get_agent_status()
        
        return {
            "status": "healthy",
            "agents_initialized": len(status.get("agents", {})) == 5,
            "agents": list(status.get("agents", {}).keys()),
            "message": "Agentic content service is healthy"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Agentic content service is unhealthy"
        }