from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models.base import *
import sentry_sdk
import logging
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.middleware import RequestLoggingMiddleware

from app.routes.auth_routes import router as auth_router
from app.routes.dataset_routes import router as dataset_router
from app.routes.upload_routes import router as upload_router
from app.routes.analytics_routes import router as analytics_router
from app.routes.chatbot_routes import router as chatbot_router
from app.routes.rag_routes import router as rag_router
from app.routes.sql_agent_routes import router as sql_agent_router
from app.routes.prediction_routes import router as prediction_router
from app.routes.health_routes import router as health_router
from app.routes.task_routes import router as task_router
from app.routes.ws_chat_routes import router as ws_chat_router
from app.routes.credit_routes import router as credit_router
from app.routes.admin_routes import router as admin_router
from app.routes.payment_routes import router as payment_router
from app.routes.payment_history_routes import router as payment_history_router
from app.routes.invoice_routes import router as invoice_router
from app.routes.ml_routes import router as ml_router
from app.routes.memory_routes import router as memory_router
#from prometheus_fastapi_instrumentator import Instrumentator

log = logging.getLogger("ai_bi_dashboard")


@asynccontextmanager
async def lifespan(app):
    """Pre-load heavy ML models once at startup — prevents 30s delay per request."""
    try:
        log.info("Pre-loading embedding model...")
        from app.services.embedding_service import get_embedding_model
        get_embedding_model()
        log.info("Embedding model ready.")
    except Exception as e:
        log.warning(f"Embedding model preload failed: {e}")

    try:
        log.info("Pre-loading reranker model...")
        from app.services.reranker_service import get_reranker
        get_reranker()
        log.info("Reranker model ready.")
    except Exception as e:
        log.warning(f"Reranker model preload failed: {e}")

    log.info("All models loaded. Server ready.")
    yield


app = FastAPI(
    title="AI BI Dashboard + RAG API",
    version="1.0.0",
    lifespan=lifespan  # ← key change
)

#Instrumentator().instrument(app).expose(app)

sentry_dsn = settings.SENTRY_DSN.strip().strip("\"'")
if sentry_dsn.startswith(("http://", "https://")):
    sentry_sdk.init(dsn=sentry_dsn, traces_sample_rate=1.0)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth_router,             prefix="/api/v1/auth",             tags=["Auth"])
app.include_router(dataset_router,          prefix="/api/v1/datasets",         tags=["Datasets"])
app.include_router(upload_router,           prefix="/api/v1/upload",           tags=["Upload"])
app.include_router(analytics_router,        prefix="/api/v1/analytics",        tags=["Analytics"])
app.include_router(chatbot_router,          prefix="/api/v1/chatbot",          tags=["Chatbot"])
app.include_router(rag_router,              prefix="/api/v1/rag",              tags=["RAG"])
app.include_router(sql_agent_router,        prefix="/api/v1/sql-agent",        tags=["SQL Agent"])
app.include_router(prediction_router,       prefix="/api/v1/predict",          tags=["Prediction"])
app.include_router(ml_router,               prefix="/api/v1/ml",               tags=["ML"])
app.include_router(credit_router,           prefix="/api/v1/credits",          tags=["Credits"])
app.include_router(payment_router,          prefix="/api/v1/payments",         tags=["Payments"])
app.include_router(payment_history_router, prefix="/api/v1/payments",          tags=["Payment History"])
app.include_router(invoice_router,          prefix="/api/v1/invoices",         tags=["Invoices"])
app.include_router(memory_router,           prefix="/api/v1/memory",           tags=["Memory"])
app.include_router(admin_router,            prefix="/api/v1/admin",            tags=["Admin"])
app.include_router(task_router,             prefix="/api/v1/tasks",            tags=["Tasks"])
app.include_router(health_router,           prefix="/api/v1/health",           tags=["Health"])
app.include_router(ws_chat_router)


# from dotenv import load_dotenv
# load_dotenv()

# from fastapi import FastAPI
# from app.models.base import *
# import sentry_sdk
# from app.config import settings
# from fastapi.middleware.cors import CORSMiddleware

# from app.routes.auth_routes import router as auth_router
# from app.routes.dataset_routes import router as dataset_router
# from app.routes.upload_routes import router as upload_router
# from app.routes.analytics_routes import router as analytics_router
# from app.routes.chatbot_routes import router as chatbot_router
# from app.routes.rag_routes import router as rag_router
# from app.routes.sql_agent_routes import router as sql_agent_router
# from app.routes.prediction_routes import router as prediction_router

# from app.routes.task_routes import router as task_router

# from app.routes.ws_chat_routes import router as ws_chat_router
# from app.routes.credit_routes import router as credit_router
# from app.routes.admin_routes import router as admin_router
# from app.routes.payment_routes import router as payment_router
# from app.routes.payment_history_routes import router as payment_history_router
# from app.routes.invoice_routes import router as invoice_router
# from prometheus_fastapi_instrumentator import Instrumentator
# from app.routes.health_routes import router as health_router
# from app.routes.ml_routes import router as ml_router
# from app.routes.memory_routes import router as memory_router
# from app.middleware import RequestLoggingMiddleware





# app = FastAPI(title="AI BI Dashboard + RAG API", version="1.0.0")
# Instrumentator().instrument(app).expose(app)

# sentry_dsn = settings.SENTRY_DSN.strip().strip("\"'")
# if sentry_dsn.startswith(("http://", "https://")):
#     sentry_sdk.init(
#         dsn=sentry_dsn,
#         traces_sample_rate=1.0
#     )

# # CORS (Frontend will call API)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3001", "http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Register routes
# app.add_middleware(RequestLoggingMiddleware)

# app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
# app.include_router(dataset_router, prefix="/api/v1/datasets", tags=["Datasets"])
# app.include_router(upload_router, prefix="/api/v1/upload", tags=["Upload"])
# app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
# app.include_router(chatbot_router, prefix="/api/v1/chatbot", tags=["Chatbot"])
# app.include_router(rag_router, prefix="/api/v1/rag", tags=["RAG"])
# app.include_router(sql_agent_router, prefix="/api/v1/sql-agent", tags=["SQL-Agent"])
# app.include_router(prediction_router, prefix="/api/v1/predict", tags=["Prediction"])
# app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
# app.include_router(task_router, prefix="/api/v1/tasks", tags=["Tasks"])
# app.include_router(ws_chat_router)
# app.include_router(credit_router, prefix="/api/v1/credits", tags=["Credits"])
# app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"]) 
# app.include_router(payment_router, prefix="/api/v1/payments", tags=["Payments"])
# app.include_router(payment_history_router, prefix="/api/v1/payments", tags=["Payments"])
# app.include_router(invoice_router, prefix="/api/v1/invoices", tags=["Invoices"])
# app.include_router(health_router, prefix="/api/v1", tags=["Health"])
# app.include_router(ml_router, prefix="/api/v1/ml", tags=["ML"])
# app.include_router(memory_router, prefix="/api/v1/memory", tags=["Memory"])
