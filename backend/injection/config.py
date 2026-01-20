import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "examsmith")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "documents")

# Mistral Configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_EMBEDDING_MODEL = os.getenv("MISTRAL_EMBEDDING_MODEL", "mistral-embed")
MISTRAL_EMBEDDING_DIM = int(os.getenv("MISTRAL_EMBEDDING_DIM", "1024"))

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Ingestion Configuration
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
FAILED_RECORDS_PATH = os.getenv("FAILED_RECORDS_PATH", "data/failed_records.json")

# Embedding & Retry Configuration (NEW - SUGGESTION)
EMBEDDING_TIMEOUT = int(os.getenv("EMBEDDING_TIMEOUT", "30"))
MAX_EMBEDDING_RETRIES = int(os.getenv("MAX_EMBEDDING_RETRIES", "3"))
RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "50000"))

# Logging Configuration (NEW - SUGGESTION)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/ingestion.log")
