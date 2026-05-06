# AI BI + RAG Dashboard (SaaS Platform)

AI BI + RAG Dashboard is a **full-stack SaaS platform** that combines **Data Analytics + Generative AI (RAG) + Text-to-SQL + ML Predictions** into one production-ready system.

Users can upload **CSV datasets** and **PDF documents**, generate analytics dashboards, ask questions via an AI chatbot, run SQL queries using natural language, and manage billing through a credit-based payment system.

---

## 🚀 Key Features

### ✅ CSV Analytics Dashboard (BI)
- Upload CSV files
- Automatically creates SQL tables from CSV
- Generates analytics KPIs + charts (Recharts)
- Filter-based insights and trend analysis

### ✅ PDF AI Chatbot (RAG System)
- PDF ingestion + chunking + embeddings
- FAISS vector store for fast retrieval
- Hybrid search (BM25 + vector search)
- Reranking for high-quality context
- Citations + confidence scoring
- Fallback response when answer not found

### ✅ Text-to-SQL Agent
- Converts natural language questions into SQL safely
- SQL validation + injection protection
- Executes query on uploaded dataset tables
- Returns structured results + explanations

### ✅ ML Predictions (Optional Module)
- Sales forecasting / churn prediction pipelines
- Model training scripts + `.pkl` saving
- Prediction API for real-time inference

### ✅ SaaS Billing & Credits
- Credit-based usage system
- Token usage logging
- Razorpay payments integration
- Payment history tracking
- PDF invoice generation

### ✅ Admin Panel
- Manage users and credits
- View payment logs
- View usage logs and API activity

### ✅ Production Ready
- Dockerized frontend + backend
- Nginx reverse proxy
- PostgreSQL database
- Redis caching / rate limiting
- WebSocket streaming chatbot responses
- CI/CD auto deploy to AWS EC2 (GitHub Actions)

---

## 🏗️ Tech Stack

### Frontend
- Next.js 15 (App Router)
- React 19
- TailwindCSS
- Recharts (Analytics charts)
- Axios
- WebSocket Streaming UI

### Backend
- FastAPI
- PostgreSQL + SQLAlchemy + Alembic
- Redis (rate limiting, caching)
- FAISS vector database
- SentenceTransformers / OpenAI Embeddings
- OpenAI / LLM APIs
- Razorpay Payments
- PDF Invoice Generation

### DevOps
- Docker + Docker Compose
- Nginx Reverse Proxy
- SSL (Certbot)
- GitHub Actions CI/CD
- AWS EC2 Deployment

---

## 📂 Folder Structure

```bash
ai-bi-rag-dashboard/
│
├── frontend/                  # Next.js frontend dashboard
│
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── routes/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── rag/
│   │   ├── ml/
│   │   ├── utils/
│   │   ├── storage/
│   │   └── main.py
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
│
├── nginx/
│   └── nginx.conf
│
├── docker-compose.yml
└── README.md