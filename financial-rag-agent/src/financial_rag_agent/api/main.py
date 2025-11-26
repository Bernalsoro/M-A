"""
FastAPI application for Financial RAG Agent.

Provides REST API endpoints for financial analysis queries.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from financial_rag_agent.agents.agent import FinancialAgent
from financial_rag_agent.config import settings

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global agent instance
agent: FinancialAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    # Startup
    global agent
    logger.info("Starting Financial RAG Agent API")
    logger.info(f"Environment: LLM={settings.llm_provider}, Model={settings.get_llm_model()}")

    try:
        agent = FinancialAgent()
        logger.info("Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        agent = None

    yield

    # Shutdown
    logger.info("Shutting down Financial RAG Agent API")


# Create FastAPI app
app = FastAPI(
    title="Financial RAG Agent API",
    description="Retrieval Augmented Generation system for financial analysis",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class AskRequest(BaseModel):
    """Request model for /ask endpoint."""

    ticker: str | None = Field(None, description="Stock ticker symbol (optional)")
    question: str = Field(..., description="Financial question to answer")
    context_limit: int | None = Field(
        None, ge=1, le=20, description="Maximum number of context documents to retrieve"
    )
    temperature: float | None = Field(None, ge=0.0, le=2.0, description="LLM temperature")


class AskResponse(BaseModel):
    """Response model for /ask endpoint."""

    answer: str = Field(..., description="Generated answer")
    question: str = Field(..., description="Original question")
    ticker: str | None = Field(None, description="Ticker symbol if provided")
    plan: dict[str, Any] = Field(..., description="Execution plan")
    used_tools: list[str] = Field(..., description="Tools executed")
    retrieved_docs: list[dict[str, Any]] | None = Field(
        None, description="Retrieved context documents"
    )
    execution_time_ms: float = Field(..., description="Total execution time in milliseconds")
    llm_available: bool = Field(..., description="Whether LLM is properly configured")


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""

    status: str = Field(..., description="Service status")
    agent_initialized: bool = Field(..., description="Whether agent is initialized")
    llm_available: bool = Field(..., description="Whether LLM is available")
    vector_store_loaded: bool = Field(..., description="Whether vector store is loaded")
    details: dict[str, Any] | None = Field(None, description="Additional status details")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")


# Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Financial RAG Agent API",
        "version": "0.1.0",
        "description": "Retrieval Augmented Generation for financial analysis",
        "endpoints": {
            "POST /ask": "Submit a financial question",
            "GET /health": "Health check",
            "GET /status": "Detailed agent status",
            "GET /docs": "OpenAPI documentation",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        Service health status
    """
    if agent is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "agent_initialized": False,
                "llm_available": False,
                "vector_store_loaded": False,
                "details": {"error": "Agent not initialized"},
            },
        )

    try:
        agent_status = agent.get_status()

        vector_store_info = agent_status.get("vector_store", {})
        vector_store_loaded = vector_store_info.get("num_documents", 0) > 0

        return {
            "status": "healthy",
            "agent_initialized": True,
            "llm_available": agent_status["llm"]["available"],
            "vector_store_loaded": vector_store_loaded,
            "details": {
                "vector_store_docs": vector_store_info.get("num_documents", 0),
                "llm_provider": agent_status["llm"]["provider"],
                "llm_model": agent_status["llm"]["model"],
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "agent_initialized": True,
                "llm_available": False,
                "vector_store_loaded": False,
                "details": {"error": str(e)},
            },
        )


@app.get("/status", tags=["Status"])
async def get_status():
    """
    Get detailed agent status and configuration.

    Returns:
        Comprehensive status information
    """
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized",
        )

    return agent.get_status()


@app.post("/ask", response_model=AskResponse, tags=["Analysis"])
async def ask_question(request: AskRequest):
    """
    Submit a financial question to the agent.

    Args:
        request: Question and optional parameters

    Returns:
        Generated answer with metadata

    Example:
        ```
        POST /ask
        {
          "ticker": "AAPL",
          "question": "What are the key financial highlights from recent earnings?"
        }
        ```
    """
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized. Check server logs for details.",
        )

    try:
        # Execute agent
        result = agent.answer(
            ticker=request.ticker,
            question=request.question,
        )

        # Check for errors
        if not result.get("success", True):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Unknown error during execution"),
            )

        # Extract retrieved documents
        retrieved_docs = []
        if "retrieve_context" in result.get("tool_results", {}):
            context_result = result["tool_results"]["retrieve_context"]
            if context_result.get("success"):
                retrieved_docs = context_result.get("documents", [])

        # Build response
        response = AskResponse(
            answer=result["final_answer"],
            question=result["question"],
            ticker=result.get("ticker"),
            plan=result.get("plan", {}),
            used_tools=result.get("used_tools", []),
            retrieved_docs=retrieved_docs if retrieved_docs else None,
            execution_time_ms=result.get("execution_time_ms", 0),
            llm_available=result.get("llm_available", False),
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}",
        )


@app.get("/tickers", tags=["Data"])
async def get_available_tickers():
    """
    Get list of available ticker symbols.

    Returns:
        List of tickers in the dataset
    """
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized",
        )

    try:
        result = agent.tools.get_available_tickers()
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve tickers",
            )

        return {
            "tickers": result["tickers"],
            "count": result["count"],
        }
    except Exception as e:
        logger.error(f"Error getting tickers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "detail": None},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.log_level == "DEBUG" else None,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "financial_rag_agent.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
