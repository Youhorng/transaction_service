import logging 
import motor.motor_asyncio
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional

from app.config.config import settings

# Global database client 
client = None
db = None

# Connect to MongoDB and initialize collections 
async def connect_to_mongodb():
    global client, db

    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DB]
        
        # Create indexes 
        await db.transactions.create_index("transaction_number", unique=True)

        logging.info("Connected to MongoDB successfully")
    
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise e
    

# Close MongoDB connection
async def close_mongodb_connection():
    global client 

    if client:
        client.close()
        logging.info("MongoDB connection closed")


# Save tranasaction to the database 
async def save_transaction(transaction: Dict) -> Dict:
    global db 

    if db is None:
        await connect_to_mongodb()

    # Add created_at timestamp if not present 
    if "created_at" not in transaction:
        transaction["created_at"] = datetime.now()

    # Insert the transaction into the database
    result = await db.transactions.insert_one(transaction)
    transaction["_id"] = str(result.inserted_id)

    return transaction


# Get a transaction by its ID
async def get_transaction_by_id(id: str) -> Optional[Dict]:
    global db

    if db is None:
        await connect_to_mongodb()

    transaction = None

    try:
        # First try to find by MongoDB ObjectId
        if len(id) == 24:  # MongoDB ObjectId is 24 hex chars
            try:
                transaction = await db.transactions.find_one({"_id": ObjectId(id)})
            except:
                pass
        
        # If not found or not a valid ObjectId, try by transaction_id
        if not transaction:
            transaction = await db.transactions.find_one({"transaction_number": id})
        
        # Convert ObjectId to string for easier handling
        if transaction:
            transaction["_id"] = str(transaction["_id"])
        
        return transaction
    except Exception as e:
        logging.error(f"Error getting transaction: {e}")
        return None
    

# Update transaction data
async def update_transaction(id: str, updates: Dict) -> bool:
    global db

    if db is None:
        await connect_to_mongodb()
    
    try:
        # Add updated_at timestamp
        updates["updated_at"] = datetime.now()
        
        # Update the transaction
        result = await db.transactions.update_one(
            {"_id": ObjectId(id)},
            {"$set": updates}
        )
        
        return result.modified_count > 0
    except Exception as e:
        logging.error(f"Error updating transaction: {e}")
        return False
    

# List all transactions
async def list_transactions(page: int = 1, limit: int = 10, filters: Dict = None) -> Dict:
    """List transactions with pagination and optional filters"""
    global db
    if db is None:
        await connect_to_mongodb()
    
    if filters is None:
        filters = {}
    
    skip = (page - 1) * limit
    
    try:
        # Get paginated transactions
        cursor = db.transactions.find(filters).sort("created_at", -1).skip(skip).limit(limit)
        transactions = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for each transaction
        for transaction in transactions:
            transaction["_id"] = str(transaction["_id"])
        
        # Get total count for pagination
        total = await db.transactions.count_documents(filters)
        
        return {
            "success": True,
            "transactions": transactions,
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit  # Ceiling division
        }
    except Exception as e:
        logging.error(f"Error listing transactions: {e}")
        return {
            "success": False,
            "error": str(e)
        }