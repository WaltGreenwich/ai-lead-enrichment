"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict
from datetime import datetime


class CompanyInput(BaseModel):
    """Input schema for company enrichment"""
    name: str = Field(..., description="Company name")
    domain: Optional[HttpUrl] = Field(None, description="Company website")


class EnrichedCompany(BaseModel):
    """Enriched company data"""
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    pain_points: Optional[List[str]] = None
    fit_score: Optional[float] = Field(None, ge=0, le=1)
    outreach_suggestions: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SearchQuery(BaseModel):
    """Semantic search query"""
    query: str = Field(..., description="Natural language search query")
    limit: int = Field(5, ge=1, le=50, description="Number of results")


class SearchResult(BaseModel):
    """Search result with similarity score"""
    company: EnrichedCompany
    similarity_score: float = Field(..., ge=0, le=1)


class EnrichmentResponse(BaseModel):
    """Response after enrichment"""
    success: bool
    company: Optional[EnrichedCompany] = None
    error: Optional[str] = None
    processing_time: float


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, bool]
