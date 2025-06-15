import logging 
import uuid
from datetime import datetime 
from typing import Dict, List, Optional, Any

from app.db.transactions import (
    save_transaction,
    get_transaction_by_id,
    update_transaction,
    list_transactions
)

from app.services.fraud_service import fraud_service
from app.services.notification_service import notification_service
from app.models.schemas import TransactionStatus


# Process new transaction with fraud detection and notification
async def process_transaction(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Generate transaction_number if not provided
        if "transaction_number" not in transaction_data:
            transaction_number = f"txn_{uuid.uuid4().hex[:8]}"
            transaction_data["transaction_number"] = transaction_number
        
        # Set initial status to pending
        transaction_data["status"] = TransactionStatus.PENDING
        transaction_data["created_at"] = datetime.now()
        
        # Save transaction with pending status
        saved_transaction = await save_transaction(transaction_data)
        
        # Call fraud detection service
        fraud_result = await fraud_service.check_transaction(transaction_data)
        
        # Initialize variables
        fraud_detected = False
        notification_result = {"notification_sent": False}
        transaction_status = TransactionStatus.APPROVED
        
        # Process fraud detection result
        if isinstance(fraud_result, dict):
            # Update transaction with fraud detection results
            update_data = {
                "fraud_check_result": fraud_result,
                "is_fraud": fraud_result.get("is_fraud", False),
                "fraud_probability": fraud_result.get("fraud_probability", 0.0)
            }
            
            # Update status based on fraud result
            if fraud_result.get("is_fraud", False):
                fraud_detected = True
                transaction_status = TransactionStatus.FLAGGED
                
                # Send fraud notification
                notification_result = await notification_service.send_fraud_notification(
                    transaction_data, fraud_result
                )
                
                if isinstance(notification_result, dict):  # Make sure it's a dict
                    update_data["notification_result"] = notification_result
                    update_data["notification_sent"] = notification_result.get("notification_sent", False)
            else:
                transaction_status = TransactionStatus.APPROVED
                
            update_data["status"] = transaction_status
            
            # THIS IS IMPORTANT - call update_transaction as a function
            await update_transaction(saved_transaction["_id"], update_data)
            
        # Get the updated transaction - THIS IS IMPORTANT
        updated_transaction = await get_transaction_by_id(saved_transaction["_id"])
        
        # Prepare response using the updated_transaction dictionary
        response = {}
        if updated_transaction:
            response = {
                "transaction_number": updated_transaction.get("transaction_number"),
                "status": updated_transaction.get("status", str(transaction_status)),
                "created_at": updated_transaction.get("created_at").isoformat() if updated_transaction.get("created_at") else None,
                "is_fraud": updated_transaction.get("is_fraud", fraud_detected),
                "fraud_probability": updated_transaction.get("fraud_probability", 
                                     fraud_result.get("fraud_probability", 0.0) if isinstance(fraud_result, dict) else 0.0),
                "notification_sent": updated_transaction.get("notification_sent", False)
            }
            
            # Add other fields from updated_transaction
            for field in ["category", "merchant_name", "transaction_amount", "transaction_location"]:
                if field in updated_transaction:
                    response[field] = updated_transaction[field]
                    
        # Return success response
        return {
            "success": True,
            "transaction": response
        }
    except Exception as e:
        import traceback
        logging.error(f"Error processing transaction: {e}")
        logging.error(traceback.format_exc())  # Print full stack trace
        return {
            "success": False,
            "error": str(e)
        }
    

async def get_transaction(id: str) -> Dict[str, Any]:
    """Get a transaction by ID or transaction_id"""
    try:
        transaction = await get_transaction_by_id(id)
        
        if not transaction:
            return {
                "success": False,
                "error": f"Transaction not found with ID: {id}"
            }
            
        # Check notification status if transaction was flagged as fraud
        if transaction.get("is_fraud", False) and transaction.get("notification_sent", False):
            notification_status = await notification_service.check_notification_status(
                transaction["transaction_id"]
            )
            
            if notification_status["success"] and notification_status.get("notification"):
                transaction["notification_status"] = notification_status["notification"]
                
        return {
            "success": True,
            "transaction": transaction
        }
        
    except Exception as e:
        logging.error(f"Error getting transaction: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def get_transactions(page: int = 1, limit: int = 10, status: Optional[str] = None) -> Dict[str, Any]:
    """Get a list of transactions with optional filtering"""
    try:
        filters = {}
        
        # Apply status filter if provided
        if status:
            filters["status"] = status
            
        result = await list_transactions(page, limit, filters)
        return result
        
    except Exception as e:
        logging.error(f"Error getting transactions: {e}")
        return {
            "success": False,
            "error": str(e)
        }