from pydantic import BaseModel, Field, validator 
from typing import Dict, List, Optional, Any
from datetime import datetime 
from enum import Enum 

class TransactionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    FLAGGED = "flagged"


class TransactionRequest(BaseModel):
    transaction_amount: float = Field(..., description="Amount of the transaction")
    is_nighttime: int = Field(..., description="1 if the transaction is made at night, 0 otherwise")
    category: str = Field(..., description="Merchant category")
    transaction_location: str = Field(..., description="Location of the transaction")
    job: str = Field(..., description="Job of the cardholder")
    state: str = Field(..., description="State where the transaction occurred")
    transaction_number: str = Field(..., description="Unique identifier for the transaction")

    model_config = {  # Updated to use model_config instead of Config class
        "json_schema_extra": {  # Changed from schema_extra to json_schema_extra
            "example": {
                "transaction_amount": 150.55,
                "is_nighttime": 1,
                "category": "shopping_pos",
                "transaction_location": "-95.7923, 36.1499",
                "job": "Naval architect",
                "state": "CA",
                "transaction_number": "txn_1001"
            }
        }
    }


class TransactionCreateResponse(BaseModel):
    transaction_number: str = Field(..., description="Unique identifier for the transaction")
    status: TransactionStatus = Field(..., description="Status of the transaction")
    created_at: datetime = Field(..., description="When the transaction was created")
    is_fraud: Optional[bool] = Field(None, description="Whether the transaction is fraudulent")
    fraud_probability: Optional[float] = Field(None, description="Probability of fraud")
    notification_sent: Optional[bool] = Field(None, description="Whether a notification was sent")
    
    class Config:
        schema_extra = {
            "example": {
                "transaction_number": "txn_1001",
                "status": "approved",
                "created_at": "2023-10-15T14:30:00.000Z",
                "is_fraud": False,
                "fraud_probability": 0.05,
                "notification_sent": False
            }
        }


class TransactionDetailResponse(TransactionCreateResponse):
    category: str = Field(..., description="Merchant category")
    transaction_amount: float = Field(..., description="Amount of the transaction")
    transaction_location: str = Field(..., description="Location of the transaction")
    job: str = Field(..., description="Job of the cardholder")
    state: str = Field(..., description="State where the transaction occurred")
    is_nighttime: str = Field(..., description="1 if the transaction is made at night, 0 otherwise")

    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "TX123456789",
                "status": "approved",
                "created_at": "2023-10-15T14:30:00.000Z",
                "is_fraud": False,
                "fraud_probability": 0.05,
                "notification_sent": False,
                "category": "shopping_pos",
                "transaction_amount": 150.55,
                "transaction_location": "-95.7923, 36.1499",
                "job": "Naval architect",
                "state": "CA",
                "is_nighttime": "1"
            }
        }


class PaginatedTransactions(BaseModel):
    success: bool = Field(..., description="Whether the request was successful")
    transactions: List[TransactionDetailResponse] = Field(..., description="List of transactions")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of transactions")
    pages: int = Field(..., description="Total number of pages")