from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
from app.db.transactions import connect_to_mongodb, close_mongodb_connection
from app.routers import transaction_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create FastAPI application
app = FastAPI(
    title="Credit Card Transaction Service",
    description="Handles credit card transactions and integrates with fraud detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(transaction_routes.router)

@app.on_event("startup")
async def startup_event():
    """Connect to database when app starts"""
    await connect_to_mongodb()
    logging.info("Transaction Service started")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection when app shuts down"""
    await close_mongodb_connection()
    logging.info("Transaction Service shutdown")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Credit Card Transaction Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "create_transaction": "/transactions/create",
            "get_transaction": "/transactions/{id}",
            "list_transactions": "/transactions/",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "ok"}

if __name__ == "__main__":
    from app.config.config import settings
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)