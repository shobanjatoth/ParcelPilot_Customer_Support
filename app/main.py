# import os
# import sys
# import logging
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager

# from app.config import get_settings
# from app.data.models import init_db, SessionLocal
# from app.data.ingestion import run_ingestion
# from app.vector.store import VectorStore

# import os

# # Inside your lifespan function in app/main.py:
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "parcelpilot-ai-agent"

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(name)s %(levelname)s %(message)s",
#     datefmt="%Y-%m-%dT%H:%M:%S",
# )
# logger = logging.getLogger("parcelpilot")

# vector_store_instance = None


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     global vector_store_instance

#     settings = get_settings()
#     logger.info(f"Starting ParcelPilot | model={settings.llm_model} db={settings.database_url[:30]}")

#     init_db()
#     vector_store_instance = VectorStore()
    
#     db = SessionLocal()
#     try:
#         run_ingestion(db, vector_store_instance)
#     finally:
#         db.close()

#     logger.info("ParcelPilot ready")
#     yield
#     logger.info("ParcelPilot shutting down")


# app = FastAPI(
#     title="ParcelPilot AI Support Agent",
#     version="1.0.0",
#     lifespan=lifespan,
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# from app.api.routes import router
# app.include_router(router)











import os
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.data.models import init_db, SessionLocal
from app.vector.store import VectorStore


# =========================================================
# Environment
# =========================================================

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "parcelpilot-ai-agent"


# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

logger = logging.getLogger("parcelpilot")


# =========================================================
# Global Vector Store
# =========================================================

vector_store_instance: VectorStore | None = None


# =========================================================
# Application Lifespan
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    global vector_store_instance

    settings = get_settings()

    logger.info(
        "Starting ParcelPilot | "
        f"model={settings.llm_model} | "
        f"environment={settings.environment}"
    )

    # -----------------------------------------------------
    # Initialize PostgreSQL
    # -----------------------------------------------------

    init_db()

    logger.info("Database initialized")

    # -----------------------------------------------------
    # Initialize Qdrant
    # -----------------------------------------------------
    #
    # VectorStore no longer loads SentenceTransformer
    # during initialization.
    #
    # The embedding model is loaded only when a search
    # or ingestion operation actually needs embeddings.
    #

    vector_store_instance = VectorStore()

    logger.info("Vector store initialized")

    # -----------------------------------------------------
    # IMPORTANT
    # -----------------------------------------------------
    #
    # DO NOT run ingestion here.
    #
    # Ingestion should be executed separately.
    #

    logger.info("ParcelPilot ready")

    yield

    # -----------------------------------------------------
    # Shutdown
    # -----------------------------------------------------

    logger.info("ParcelPilot shutting down")


# =========================================================
# FastAPI Application
# =========================================================

app = FastAPI(
    title="ParcelPilot AI Support Agent",
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# CORS
# =========================================================

settings = get_settings()

cors_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# API Routes
# =========================================================

from app.api.routes import router
<<<<<<< ours

app.include_router(router)
=======
app.include_router(router)












# import os
# import logging
# from contextlib import asynccontextmanager

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.config import get_settings
# from app.data.models import init_db, SessionLocal
# from app.data.ingestion import run_ingestion
# from app.vector.store import VectorStore


# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "parcelpilot-ai-agent"

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(name)s %(levelname)s %(message)s",
# )

# logger = logging.getLogger("parcelpilot")

# vector_store_instance = None


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     global vector_store_instance

#     settings = get_settings()

#     logger.info("Starting ParcelPilot AI Support Agent")
#     logger.info(f"Environment: {settings.environment}")

#     # PostgreSQL
#     init_db()

#     # Qdrant + Jina
#     vector_store_instance = VectorStore()

#     # Ingestion
#     db = SessionLocal()

#     try:
#         run_ingestion(
#             db,
#             vector_store_instance
#         )
#     finally:
#         db.close()

#     logger.info("ParcelPilot API ready")

#     yield

#     logger.info("ParcelPilot shutting down")


# app = FastAPI(
#     title="ParcelPilot AI Support Agent",
#     version="1.0.0",
#     lifespan=lifespan,
# )


# # ============================================================
# # CORS
# # ============================================================

# settings = get_settings()

# origins = [
#     origin.strip()
#     for origin in settings.cors_origins.split(",")
#     if origin.strip()
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ============================================================
# # Routes
# # ============================================================

# from app.api.routes import router

# app.include_router(router)
>>>>>>> theirs
