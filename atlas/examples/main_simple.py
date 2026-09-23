"""
Mathematics AI - Simple FastAPI Application
Minimal version for debugging
"""

from fastapi import FastAPI
from app.routers import arithmetic

# Create FastAPI app
app = FastAPI(
    title="Mathematics AI - Simple",
    description="Minimal version for debugging",
    version="1.0.0"
)

# Include only basic router
app.include_router(arithmetic.router, prefix="/api/arithmetic", tags=["arithmetic"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Mathematics AI Simple Server", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0-simple"}

if __name__ == "__main__":
    import uvicorn
    print("Starting simple Mathematics AI server...")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
