import os
from pydantic_settings import BaseSettings  # type: ignore # Updated import
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Server settings
    PORT: int = int(os.getenv("PORT", 8002))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # MongoDB settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/transaction_service")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "transaction_service")  # Match .env variable name
    
    # External service URLs
    FRAUD_API_URL: str = os.getenv("FRAUD_API_URL", "http://localhost:8000")
    NOTIFY_API_URL: str = os.getenv("NOTIFY_API_URL", "http://localhost:8003")
    
    # Fraud detection settings
    FRAUD_THRESHOLD: float = float(os.getenv("FRAUD_THRESHOLD", 0.5))
    
    model_config = {  # Updated from Config class
        "env_file": ".env"
    }

settings = Settings()