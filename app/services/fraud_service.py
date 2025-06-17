import httpx 
import logging 
from typing import Dict, Optional, Any 
from app.config.config import settings


# Service to interact with the fraud detection API
class FraudService:

    # Initialize the service with API
    def __init__(self):
        self.api_url = settings.FRAUD_API_URL
        # Increase timeout from 10.0 to 60.0 seconds
        self.timeout = 60.0  # Changed from 10.0 seconds
        logging.info(f"Fraud service initialized with URL: {self.api_url}, timeout: {self.timeout}s")

    
    # Check if a transaction is fraudulent 
    async def check_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Map transaction data to the expected API format
            request_data = {
                "transaction_amount": transaction_data["transaction_amount"],
                "is_nighttime": transaction_data["is_nighttime"],
                "category": transaction_data["category"],
                "transaction_location": transaction_data["transaction_location"],
                "job": transaction_data["job"],
                "state": transaction_data["state"],
                "transaction_number": transaction_data["transaction_number"]
            }

            logging.info(f"Sending fraud check request for transaction {transaction_data['transaction_number']}")

            # Make API call to fraud service with increased timeout
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/predict",  # Removed 'fraud/' prefix since it's already in the URL
                    json=request_data,
                    timeout=self.timeout
                )

                # Check for successful response 
                if response.status_code == 200:
                    result = response.json()
                    logging.info(f"Fraud check result: {result}")

                    return {
                        "success": True,
                        "is_fraud": result.get("is_fraud", False),
                        "fraud_probability": result.get("fraud_probability", 0.0),
                        "label": result.get("label", "Unknown"),
                        "timestamp": result.get("timestamp", None)
                    }
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    logging.error(f"Fraud API error: {response.status_code} - {error_detail}")

                    return {
                        "success": False,
                        "error": f"Fraud API returned {response.status_code}: {error_detail}"
                    }
        
        except httpx.TimeoutException:
            error_msg = f"Timeout connecting to Fraud API ({self.timeout}s)"
            logging.error(error_msg)
            return {"success": False, "error": error_msg, "is_fraud": False, "fraud_probability": 0.0}
            
        except httpx.RequestError as e:
            error_msg = f"Error connecting to Fraud API: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg, "is_fraud": False, "fraud_probability": 0.0}
            
        except Exception as e:
            error_msg = f"Unexpected error in fraud check: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg, "is_fraud": False, "fraud_probability": 0.0}

fraud_service = FraudService()