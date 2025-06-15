import httpx 
import logging 
from typing import Dict, Optional, Any
from app.config.config import settings


# Service to interact with the notification API
class NotificationService:

    # Initialize API url 
    def __init__(self):
        self.api_url = settings.NOTIFY_API_URL
        self.timeout = 10.0

    
    # Send a fraud notification 
    async def send_fraud_notification(self, transaction_data: Dict[str, Any], 
                                      fraud_result: Dict[str, Any]) -> Dict[str, Any]:
        
        try: 
            # Only send notification if fraud is detected 
            if not fraud_result.get("is_fraud", False):
                return {
                    "success": True,
                    "message": "No fraud detected, notification not sent.",
                    "notification_sent": False
                }
        
            # Prepare notification data
            notification_data = {
                "transaction_number": transaction_data["transaction_number"],
                "transaction_amount": transaction_data["transaction_amount"],
                "fraud_probability": fraud_result["fraud_probability"],
                "is_nighttime": transaction_data["is_nighttime"],
                "category": transaction_data["category"],
                "transaction_location": transaction_data["transaction_location"],
                "job": transaction_data.get("cardholder_info", {}).get("job"),
                "state": transaction_data.get("cardholder_info", {}).get("state")
            }
            
            logging.info(f"Sending fraud notification for transaction {notification_data['transaction_number']}")
            
            # Make API call to notification service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/notifications/send", 
                    json=notification_data,
                    timeout=self.timeout
                )
                
                # Check for successful response
                if response.status_code in (200, 201):
                    result = response.json()
                    logging.info(f"Notification sent: {result}")
                    return {
                        "success": True,
                        "notification_number": result.get("_id"),
                        "status": result.get("status"),
                        "message": "Fraud notification sent successfully",
                        "notification_sent": True
                    }
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    logging.error(f"Notification API error: {response.status_code} - {error_detail}")
                    return {
                        "success": False,
                        "error": f"Notification API returned {response.status_code}: {error_detail}",
                        "notification_sent": False
                    }
                    
        except httpx.TimeoutException:
            error_msg = f"Timeout connecting to Notification API ({self.timeout}s)"
            logging.error(error_msg)
            return {"success": False, "error": error_msg, "notification_sent": False}
            
        except httpx.RequestError as e:
            error_msg = f"Error connecting to Notification API: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg, "notification_sent": False}
            
        except Exception as e:
            error_msg = f"Unexpected error sending notification: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg, "notification_sent": False}
            
    async def check_notification_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check the status of a notification for a transaction"""
        try:
            # Make API call to notification service
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/notifications/status/{transaction_id}",
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return {"success": True, "notification": response.json()}
                elif response.status_code == 404:
                    return {"success": True, "notification": None}
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    return {
                        "success": False,
                        "error": f"Notification API returned {response.status_code}: {error_detail}"
                    }
                    
        except Exception as e:
            error_msg = f"Error checking notification status: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}

notification_service = NotificationService()