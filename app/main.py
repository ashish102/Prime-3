"""
Prime Math API - FastAPI application for number theory operations.

This module provides REST endpoints for:
- Primality testing
- Integer factorization
- Arithmetic progression analysis
"""

from fastapi import FastAPI

app = FastAPI(
    title="Prime Math API",
    description="High-performance FastAPI service for number theory operations",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Prime Math API",
        "version": "0.1.0",
        "docs_url": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)