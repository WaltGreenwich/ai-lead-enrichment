"""
AI-powered company analysis using Google Gemini
"""
import google.generativeai as genai
from typing import Dict, Optional
import json

from config import settings


class AIAnalyzer:
    """Analyzes company data using Google Gemini AI"""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Using gemini-1.5-flash which is free and fast
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def analyze_company(
        self,
        name: str,
        website_data: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Analyze company and extract structured insights

        Returns dict with:
        - industry
        - company_size
        - description
        - tech_stack
        - pain_points
        - fit_score
        - outreach_suggestions
        """

        # Build context
        context = f"Company: {name}\n"
        if website_data:
            context += f"Website: {website_data.get('url', 'N/A')}\n"
            context += f"Title: {website_data.get('title', 'N/A')}\n"
            context += f"Description: {website_data.get('description', 'N/A')}\n"
            context += f"Content: {website_data.get('text_content', 'N/A')[:1000]}\n"

        prompt = f"""Analyze this company and provide structured insights.

{context}

Provide a JSON response with:
- industry: The company's primary industry
- company_size: Estimated size (Startup/Small/Medium/Large/Enterprise)
- description: Brief 2-sentence description
- tech_stack: Array of technologies they likely use (max 5)
- pain_points: Array of potential business pain points (max 3)
- fit_score: Score 0-1 indicating how good a lead this is (0.7+ is excellent)
- outreach_suggestions: One personalized outreach angle

Respond ONLY with valid JSON, no markdown or explanation."""

        try:
            # Gemini API call (synchronous but we can wrap it)
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.7
                )
            )

            # Parse response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            analysis = json.loads(response_text.strip())

            return analysis

        except Exception as e:
            print(f"AI analysis failed: {str(e)}")
            # Return default structure
            return {
                "industry": "Unknown",
                "company_size": "Unknown",
                "description": f"Company information for {name}",
                "tech_stack": [],
                "pain_points": [],
                "fit_score": 0.5,
                "outreach_suggestions": "Research company further before outreach"
            }
