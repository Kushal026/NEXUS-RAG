"""
API Endpoints for Phase 9 — NEXUS Research Agent.
Provides autonomous research orchestration, research planning, and gap detection endpoints.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from app.domain.models import (
    ResearchGoalRequest,
    ResearchAgentReportResult,
    ResearchPlan
)
from app.services.research_agent_service import ResearchAgentService
from app.infrastructure.agent.research_planner import ResearchPlanner
from app.core.logging import logger

router = APIRouter(prefix="/agent", tags=["NEXUS Research Agent"])

agent_service = ResearchAgentService()
planner = ResearchPlanner()


@router.post("/research", response_model=ResearchAgentReportResult)
def execute_research_goal(request: ResearchGoalRequest):
    """
    Executes an autonomous, multi-step research workflow on a user research goal,
    coordinating hybrid retrieval, graph traversal, NLI contradiction analysis,
    gap detection, and 9-section report generation.
    """
    if not request.goal.strip():
        raise HTTPException(status_code=400, detail="Research goal cannot be empty.")

    return agent_service.execute_research(request)


@router.post("/plan", response_model=ResearchPlan)
def generate_research_plan(goal: str = Body(..., embed=True)):
    """
    Generates an initial research plan with analytical sub-questions, identified entities, and hypotheses.
    """
    if not goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty.")

    return planner.generate_plan(goal)
