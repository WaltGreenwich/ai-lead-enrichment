"""
FastAPI main application
AI-Powered Lead Enrichment Pipeline
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
from typing import List
import io
import pandas as pd

from config import settings
from models.schemas import (
    CompanyInput,
    EnrichedCompany,
    EnrichmentResponse,
    SearchQuery,
    SearchResult,
    HealthCheck
)
from services.enrichment import EnrichmentService
from services.vector_db import VectorDBService


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, cleanup on shutdown"""
    # Startup
    print("🚀 Starting AI Lead Enrichment Pipeline...")
    app.state.enrichment_service = EnrichmentService()
    app.state.vector_db = VectorDBService()

    yield

    # Shutdown
    print("👋 Shutting down gracefully...")


# Initialize FastAPI app
app = FastAPI(
    title="AI Lead Enrichment Pipeline",
    description="Intelligent lead enrichment with AI analysis and semantic search",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthCheck)
async def root():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        services={
            "api": True,
            "enrichment": True,
            "vector_db": app.state.vector_db.health_check()
        }
    )


@app.post("/enrich", response_model=EnrichmentResponse)
async def enrich_company(company: CompanyInput):
    """
    Enrich a single company with AI-powered analysis

    Process:
    1. Web scraping (if domain provided)
    2. AI analysis with Gemini
    3. Generate embeddings
    4. Store in vector database
    """
    start_time = time.time()

    try:
        # Enrich company data
        enriched = await app.state.enrichment_service.enrich_company(
            name=company.name,
            domain=str(company.domain) if company.domain else None
        )

        # Store in vector DB
        await app.state.vector_db.add_company(enriched)

        processing_time = time.time() - start_time

        return EnrichmentResponse(
            success=True,
            company=enriched,
            processing_time=processing_time
        )

    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"Enrichment failed: {str(e)}"
        )


@app.post("/enrich/batch")
async def enrich_batch(file: UploadFile = File(...)):
    """
    Enrich multiple companies from CSV file

    CSV format: name,domain
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be CSV")

    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        if 'name' not in df.columns:
            raise HTTPException(400, "CSV must have 'name' column")

        # Process each company
        results = []
        for _, row in df.iterrows():
            try:
                enriched = await app.state.enrichment_service.enrich_company(
                    name=row['name'],
                    domain=row.get('domain')
                )
                await app.state.vector_db.add_company(enriched)
                results.append({"success": True, "company": enriched.name})
            except Exception as e:
                results.append(
                    {"success": False, "company": row['name'], "error": str(e)})

        return {
            "total": len(df),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }

    except Exception as e:
        raise HTTPException(500, f"Batch processing failed: {str(e)}")


@app.post("/search", response_model=List[SearchResult])
async def semantic_search(query: SearchQuery):
    """
    Semantic search across enriched companies

    Example: "fintech startups in Latin America"
    Returns: Similar companies based on embeddings
    """
    try:
        results = await app.state.vector_db.search(
            query=query.query,
            limit=query.limit
        )
        return results

    except Exception as e:
        raise HTTPException(500, f"Search failed: {str(e)}")


@app.get("/companies", response_model=List[EnrichedCompany])
async def list_companies(limit: int = 50):
    """List all enriched companies"""
    try:
        companies = await app.state.vector_db.list_all(limit=limit)
        return companies
    except Exception as e:
        raise HTTPException(500, f"Failed to list companies: {str(e)}")


@app.delete("/companies/{company_name}")
async def delete_company(company_name: str):
    """Delete a company from the database"""
    try:
        await app.state.vector_db.delete_company(company_name)
        return {"success": True, "message": f"Deleted {company_name}"}
    except Exception as e:
        raise HTTPException(500, f"Delete failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
