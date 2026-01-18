Creating AI Lead Enrichment Pipeline 🚀

Que hace?

Sistema completo de enrichment de leads que:
1. Toma lista de empresas (CSV o API)
2. Enriquece con web scraping + APIs
3. Analiza con AI (Claude)
4. Genera embeddings y guarda en vector DB
5. Permite búsqueda semántica
6. Dashboard React para visualizar

[Input CSV/Webhook]
    ↓
[n8n Workflow - Orchestration]
    ↓
├─→ [Web Scraping: Company website]
├─→ [API Enrichment: Clearbit/Apollo]
└─→ [Social Search: LinkedIn info]
    ↓
[AI Analysis - Claude/GPT]
├─→ Extract: industry, size, tech stack
├─→ Analyze: pain points, fit score
└─→ Generate: outreach suggestions
    ↓
[Vector Database - ChromaDB]
├─→ Store embeddings
└─→ Enable semantic search
    ↓
[PostgreSQL - Structured Data]
    ↓
[Dashboard - React]
└─→ Search leads semantically
└─→ View enriched data
└─→ Export for CRM

Estructura

ai-lead-enrichment/
├── README.md
├── .gitignore
├── docker-compose.yml
├── .env.example
│
├── backend/                    # FastAPI + AI logic
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── enrichment.py
│   │   ├── ai_analyzer.py
│   │   └── vector_db.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── scraper.py
│   └── tests/
│       ├── __init__.py
│       ├── test_enrichment.py
│       └── test_ai_analyzer.py
│
├── n8n/                        # Workflows
│   └── lead-enrichment-workflow.json
│
├── frontend/                   # React dashboard
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── services/
│   └── public/
│
├── database/
│   └── init.sql
│
├── demo/
│   ├── sample_leads.csv
│   ├── test_pipeline.sh
│   └── test_search.sh
│
└── docs/
    ├── architecture.md
    ├── api.md
    └── screenshots/

Tecnologias

Automation Layer:
- n8n (orchestration)
- Python scripts (custom logic)

AI Layer:
- Claude/OpenAI API (analysis)
- sentence-transformers (embeddings)
- ChromaDB (vector storage)

Data Layer:
- PostgreSQL (structured data)
- ChromaDB (semantic search)

Frontend:
- React (search interface)
- Recharts (data visualization)

Integration:
- Web scraping (Playwright/BeautifulSoup)
- APIs (Clearbit, Apollo - o mock)


