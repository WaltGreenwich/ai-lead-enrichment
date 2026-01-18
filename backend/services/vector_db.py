"""
Vector database operations using ChromaDB
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import json

from config import settings
from models.schemas import EnrichedCompany, SearchResult


class VectorDBService:
    """Manages vector database for semantic search"""

    def __init__(self):
        # Initialize ChromaDB
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False
        ))

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"description": "Enriched company data"}
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print(
            f"✅ Vector DB initialized. Collection: {self.collection.count()} documents")

    def _create_document_text(self, company: EnrichedCompany) -> str:
        """Create searchable text from company data"""
        parts = [
            f"Company: {company.name}",
            f"Industry: {company.industry or 'Unknown'}",
            f"Size: {company.company_size or 'Unknown'}",
            f"Description: {company.description or ''}",
        ]

        if company.tech_stack:
            parts.append(f"Tech: {', '.join(company.tech_stack)}")

        if company.pain_points:
            parts.append(f"Pain points: {', '.join(company.pain_points)}")

        return " | ".join(parts)

    async def add_company(self, company: EnrichedCompany):
        """Add enriched company to vector database"""
        try:
            # Create document text
            doc_text = self._create_document_text(company)

            # Generate embedding
            embedding = self.embedding_model.encode(doc_text).tolist()

            # Store in ChromaDB
            self.collection.add(
                ids=[company.name],
                embeddings=[embedding],
                documents=[doc_text],
                metadatas=[{
                    "name": company.name,
                    "domain": company.domain or "",
                    "industry": company.industry or "",
                    "company_size": company.company_size or "",
                    "fit_score": company.fit_score or 0.5,
                    "raw_data": json.dumps(company.dict(), default=str)
                }]
            )

            print(f"✅ Added {company.name} to vector DB")

        except Exception as e:
            print(f"❌ Failed to add {company.name}: {str(e)}")
            raise

    async def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Semantic search for companies"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )

            # Parse results
            search_results = []

            if results['ids'] and results['ids'][0]:
                for i, company_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if results['distances'] else 0

                    # Convert distance to similarity score (0-1)
                    similarity = 1 / (1 + distance)

                    # Parse raw data
                    raw_data = json.loads(metadata['raw_data'])
                    company = EnrichedCompany(**raw_data)

                    search_results.append(SearchResult(
                        company=company,
                        similarity_score=similarity
                    ))

            return search_results

        except Exception as e:
            print(f"Search failed: {str(e)}")
            return []

    async def list_all(self, limit: int = 50) -> List[EnrichedCompany]:
        """List all companies in database"""
        try:
            results = self.collection.get(limit=limit)

            companies = []
            if results['metadatas']:
                for metadata in results['metadatas']:
                    raw_data = json.loads(metadata['raw_data'])
                    companies.append(EnrichedCompany(**raw_data))

            return companies

        except Exception as e:
            print(f"List failed: {str(e)}")
            return []

    async def delete_company(self, company_name: str):
        """Delete company from database"""
        try:
            self.collection.delete(ids=[company_name])
            print(f"✅ Deleted {company_name}")
        except Exception as e:
            print(f"Delete failed: {str(e)}")
            raise

    def health_check(self) -> bool:
        """Check if vector DB is healthy"""
        try:
            self.collection.count()
            return True
        except:
            return False
