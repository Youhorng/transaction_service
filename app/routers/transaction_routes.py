from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List

from app.models.schemas import (
    TransactionRequest,
    TransactionCreateResponse,
    TransactionDetailResponse,
    PaginatedTransactions,
    TransactionStatus
)
from app.controllers.transaction_controller import (
    process_transaction,
    get_transaction,
    get_transactions
)

# Create Router
router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("/create", response_model=TransactionCreateResponse)
async def create_transaction(request: TransactionRequest):
    """
    Process a new credit card transaction, check for fraud, and send notification if needed
    """
    result = await process_transaction(request.dict())
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result["transaction"]

@router.get("/{id}", response_model=TransactionDetailResponse)
async def get_transaction_by_id(id: str = Path(..., description="Transaction ID")):
    """
    Get details of a specific transaction by ID
    """
    result = await get_transaction(id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result["transaction"]

@router.get("/", response_model=PaginatedTransactions)
async def list_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by transaction status")
):
    """
    List all transactions with pagination and optional filtering
    """
    if status and status not in [e.value for e in TransactionStatus]:
        valid_statuses = ", ".join([e.value for e in TransactionStatus])
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
        
    result = await get_transactions(page, limit, status)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result