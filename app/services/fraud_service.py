import httpx 
import logging 
from typing import Dict, Optional, Any 
from app.config.config import settings


# Service to interact with the fraud detection API
class FraudService:

    # Inialize the sevice with API
    def __init__(self):
        self.api_url = settings.FRAUD_API_URL
        self.timeout = 10.0

    
    # Check if a transaction if fraudulent 
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

            # Make API call to fraud service 
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/fraud/predict",
                    json=request_data,
                    timeout=self.timeout
                )

                # Check for successful response 
                if response.status_code == 200:
                    result = response.json()
                    logging.info(f"Fraud check result: {result}")

                    return {
                        "success": True,
                        "is_fraud": result["is_fraud"],
                        "fraud_probability": result["fraud_probability"],
                        "label": result["label"],
                        "timestamp": result["timestamp"]
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
            return {"success": False, "error": error_msg}
            
        except httpx.RequestError as e:
            error_msg = f"Error connecting to Fraud API: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error in fraud check: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}

fraud_service = FraudService()