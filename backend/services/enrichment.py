"""
Main enrichment service orchestrating all steps
"""
from typing import Optional
from datetime import datetime

from models.schemas import EnrichedCompany
from utils.scraper import WebScraper
from services.ai_analyzer import AIAnalyzer


class EnrichmentService:
    """Orchestrates company enrichment process"""

    def __init__(self):
        self.scraper = WebScraper()
        self.ai_analyzer = AIAnalyzer()

    async def enrich_company(
        self,
        name: str,
        domain: Optional[str] = None
    ) -> EnrichedCompany:
        """
        Complete enrichment pipeline:
        1. Scrape website (if domain provided)
        2. Analyze with AI
        3. Return enriched data
        """
        print(f"🔍 Enriching: {name}")

        # Step 1: Scrape website
        website_data = None
        if domain:
            print(f"  📄 Scraping {domain}...")
            website_data = await self.scraper.scrape_website(domain)

        # Step 2: AI Analysis
        print(f"  🤖 AI analyzing...")
        analysis = await self.ai_analyzer.analyze_company(name, website_data)

        # Step 3: Build enriched company object
        enriched = EnrichedCompany(
            name=name,
            domain=domain,
            industry=analysis.get('industry'),
            company_size=analysis.get('company_size'),
            description=analysis.get('description'),
            tech_stack=analysis.get('tech_stack', []),
            pain_points=analysis.get('pain_points', []),
            fit_score=analysis.get('fit_score', 0.5),
            outreach_suggestions=analysis.get('outreach_suggestions'),
            created_at=datetime.utcnow()
        )

        print(f"  ✅ Enriched: {name} (Score: {enriched.fit_score})")

        return enriched
