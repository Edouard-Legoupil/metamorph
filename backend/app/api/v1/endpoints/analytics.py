"""
Analytics Endpoints

Provides comprehensive analytics and insights across the Metamorph platform.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.services.analytics_service import AnalyticsService

# Initialize analytics service
analytics_service = AnalyticsService()

router = APIRouter(prefix="/analytics", tags=["analytics"])


class TimeRangeRequest(BaseModel):
    """Request model for time-range based analytics"""
    days: int = 30


@router.get("/health", response_model=Dict[str, Any])
async def analytics_health() -> Dict[str, Any]:
    """
    Check analytics service health
    
    Returns basic health information about the analytics service.
    """
    return {
        "status": "healthy",
        "service": "analytics",
        "message": "Analytics service is operational"
    }


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_comprehensive_dashboard() -> Dict[str, Any]:
    """
    Get comprehensive analytics dashboard
    
    Returns a complete dashboard with all key metrics, trends, and insights
    across the entire platform.
    """
    try:
        dashboard = analytics_service.get_comprehensive_dashboard()
        return {
            "success": True,
            "data": dashboard,
            "message": "Comprehensive analytics dashboard generated successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dashboard: {str(e)}"
        )


@router.get("/content/quality", response_model=Dict[str, Any])
async def get_content_quality_metrics() -> Dict[str, Any]:
    """
    Get content quality metrics
    
    Returns comprehensive quality metrics for knowledge cards including:
    - Status distribution
    - Card type distribution
    - Confidence scores
    - Source quality
    - Temporal coverage
    """
    try:
        metrics = analytics_service.get_content_quality_metrics()
        return {
            "success": True,
            "data": metrics,
            "message": "Content quality metrics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get content quality metrics: {str(e)}"
        )


@router.get("/wiki/quality", response_model=Dict[str, Any])
async def get_wiki_quality_metrics() -> Dict[str, Any]:
    """
    Get wiki block quality metrics
    
    Returns quality metrics for wiki blocks including verification status,
    block types, confidence scores, and live vs draft distribution.
    """
    try:
        metrics = analytics_service.get_wiki_block_quality_metrics()
        return {
            "success": True,
            "data": metrics,
            "message": "Wiki quality metrics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get wiki quality metrics: {str(e)}"
        )


@router.get("/system/usage", response_model=Dict[str, Any])
async def get_system_usage_stats() -> Dict[str, Any]:
    """
    Get system usage statistics
    
    Returns overall system usage statistics including content counts,
    user statistics, collaboration metrics, and ingestion statistics.
    """
    try:
        stats = analytics_service.get_system_usage_stats()
        return {
            "success": True,
            "data": stats,
            "message": "System usage statistics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system usage stats: {str(e)}"
        )


@router.get("/validation/metrics", response_model=Dict[str, Any])
async def get_validation_workflow_metrics() -> Dict[str, Any]:
    """
    Get validation workflow metrics
    
    Returns metrics about the validation workflow including status distribution,
    processing times, and validation quality indicators.
    """
    try:
        metrics = analytics_service.get_validation_workflow_metrics()
        return {
            "success": True,
            "data": metrics,
            "message": "Validation workflow metrics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get validation metrics: {str(e)}"
        )


@router.get("/discussion/metrics", response_model=Dict[str, Any])
async def get_discussion_activity_metrics() -> Dict[str, Any]:
    """
    Get discussion activity metrics
    
    Returns metrics about discussion thread activity including thread counts,
    comment activity, resolution rates, and engagement metrics.
    """
    try:
        metrics = analytics_service.get_discussion_activity_metrics()
        return {
            "success": True,
            "data": metrics,
            "message": "Discussion activity metrics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get discussion metrics: {str(e)}"
        )


@router.get("/ingestion/metrics", response_model=Dict[str, Any])
async def get_ingestion_pipeline_metrics() -> Dict[str, Any]:
    """
    Get ingestion pipeline metrics
    
    Returns metrics about the ingestion pipeline performance including
    website statistics, scraping success rates, and ingestion job metrics.
    """
    try:
        metrics = analytics_service.get_ingestion_pipeline_metrics()
        return {
            "success": True,
            "data": metrics,
            "message": "Ingestion pipeline metrics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get ingestion metrics: {str(e)}"
        )


@router.post("/trends/content", response_model=Dict[str, Any])
async def get_content_growth_trends(
    request: TimeRangeRequest = Body(...)
) -> Dict[str, Any]:
    """
    Get content growth trends
    
    Returns time-series data for content growth over a specified time period.
    
    Args:
        request: TimeRangeRequest with days parameter (default: 30)
        
    Returns:
        Daily statistics for knowledge cards and wiki blocks created
        within the specified time range.
    """
    try:
        trends = analytics_service.get_content_growth_trends(request.days)
        return {
            "success": True,
            "data": trends,
            "message": f"Content growth trends for last {request.days} days retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get content growth trends: {str(e)}"
        )


@router.post("/trends/validation", response_model=Dict[str, Any])
async def get_validation_activity_trends(
    request: TimeRangeRequest = Body(...)
) -> Dict[str, Any]:
    """
    Get validation activity trends
    
    Returns time-series data for validation activity over a specified time period.
    
    Args:
        request: TimeRangeRequest with days parameter (default: 30)
        
    Returns:
        Daily statistics for validation cards by status within the specified time range.
    """
    try:
        trends = analytics_service.get_validation_activity_trends(request.days)
        return {
            "success": True,
            "data": trends,
            "message": f"Validation activity trends for last {request.days} days retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get validation trends: {str(e)}"
        )


@router.get("/key-insights", response_model=Dict[str, Any])
async def get_key_insights() -> Dict[str, Any]:
    """
    Get key insights
    
    Returns automatically generated key insights based on current system state.
    These insights highlight important patterns, achievements, and areas
    needing attention.
    """
    try:
        # Get the metrics needed for insights
        content_quality = analytics_service.get_content_quality_metrics()
        validation_metrics = analytics_service.get_validation_workflow_metrics()
        ingestion_metrics = analytics_service.get_ingestion_pipeline_metrics()
        
        insights = analytics_service._generate_key_insights(
            content_quality, validation_metrics, ingestion_metrics
        )
        
        return {
            "success": True,
            "insights": insights,
            "count": len(insights),
            "message": "Key insights generated successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate key insights: {str(e)}"
        )