"""
AI Support Service - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional
import logging
import time
import os
from app.rag.pipeline import ask
from app.observability import metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Support Service",
    description="Backend API for AI-powered support system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Pydantic models
class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The question to be answered by the AI support system"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "question": "How do I reset my password?"
            }
        }


class AnswerResponse(BaseModel):
    """Response model for answers"""
    answer: str = Field(
        ...,
        description="The AI-generated answer to the question"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "placeholder response"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(
        ...,
        description="Health status of the service"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok"
            }
        }


# Endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns:
        HealthResponse: Status of the service
    """
    logger.info("Health check requested")
    return HealthResponse(status="ok")


@app.post("/ask", response_model=AnswerResponse, tags=["Support"])
async def ask_question(request: QuestionRequest):
    """
    Ask a question to the AI support system

    Args:
        request: QuestionRequest containing the question

    Returns:
        AnswerResponse: AI-generated answer

    Raises:
        HTTPException: If question processing fails
    """
    start_time = time.time()
    error_type = None

    try:
        logger.info(f"Question received: {request.question[:50]}...")

        # Use RAG pipeline to generate answer
        with metrics.MetricsTimer(metrics.rag_pipeline_latency):
            answer = ask(request.question)

        # Record successful request
        latency = time.time() - start_time
        metrics.request_latency_seconds.labels(endpoint="/ask").observe(latency)
        metrics.record_request(endpoint="/ask", method="POST", status="success")

        logger.info("Answer generated successfully")
        return AnswerResponse(answer=answer)

    except ValueError as ve:
        # Configuration error (e.g., missing API key)
        error_type = "configuration_error"
        logger.error(f"Configuration error: {str(ve)}")
        metrics.record_failure(endpoint="/ask", error_type=error_type)
        metrics.record_request(endpoint="/ask", method="POST", status="error")
        raise HTTPException(
            status_code=503,
            detail="Service not properly configured. Please check API keys."
        )
    except Exception as e:
        # General error
        error_type = type(e).__name__
        logger.error(f"Error processing question: {str(e)}")
        metrics.record_failure(endpoint="/ask", error_type=error_type)
        metrics.record_request(endpoint="/ask", method="POST", status="error")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question"
        )


@app.get("/metrics", tags=["Observability"])
async def get_metrics():
    """
    Prometheus metrics endpoint

    Returns:
        Response: Prometheus metrics in text format
    """
    metrics_data, content_type = metrics.get_metrics()
    return Response(content=metrics_data, media_type=content_type)


@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    """
    Root endpoint - serves the interactive web interface

    Returns:
        FileResponse: The main HTML page
    """
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        # Fallback to JSON if HTML file doesn't exist
        return {
            "message": "Welcome to AI Support Service API",
            "documentation": "/docs",
            "health": "/health",
            "metrics": "/metrics"
        }


@app.get("/api", tags=["Root"])
async def api_info():
    """
    API information endpoint

    Returns:
        dict: API information and available endpoints
    """
    return {
        "message": "Welcome to AI Support Service API",
        "version": "1.0.0",
        "endpoints": {
            "interactive_ui": "/",
            "documentation": "/docs",
            "health": "/health",
            "ask": "/ask",
            "metrics": "/metrics"
        }
    }


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup"""
    logger.info("AI Support Service starting up...")
    # TODO: Initialize AI model, database connections, etc.


@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform on application shutdown"""
    logger.info("AI Support Service shutting down...")
    # TODO: Close connections, cleanup resources


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
