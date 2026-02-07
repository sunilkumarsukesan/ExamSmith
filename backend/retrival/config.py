from pydantic_settings import BaseSettings
from pydantic import Field
import os
from pathlib import Path

# Load .env from project root
project_root = Path(__file__).parent.parent.parent  # Go up 3 levels to project root
env_file_path = project_root / ".env"

class Settings(BaseSettings):
    """Load configuration from .env in project root"""
    
    # MongoDB
    mongodb_uri: str = Field("", alias="MONGODB_URI")
    mongodb_db_textbook: str = Field("10_books", alias="MONGODB_BOOKS_DB")
    mongodb_collection_textbook: str = Field("english", alias="MONGODB_BOOKS_COLLECTION")
    mongodb_db_questionpapers: str = Field("10_questionpapers", alias="MONGODB_QUESTIONPAPERS_DB")
    mongodb_collection_questionpapers: str = Field("2025_public", alias="MONGODB_QUESTIONPAPERS_COLLECTION")
    
    # Groq
    groq_api_key: str = Field("", alias="GROQ_API_KEY")
    groq_model: str = Field("meta-llama/llama-4-maverick-17b-128e-instruct", alias="GROQ_MODEL")
    
    # Mistral Embeddings (for semantic search)
    mistral_api_key: str = Field("", alias="MISTRAL_API_KEY")
    mistral_embed_model: str = Field("mistral-embed", alias="MISTRAL_EMBED_MODEL")
    mistral_embed_dimension: int = Field(1024, alias="MISTRAL_EMBED_DIMENSION")
    
    # FastAPI
    fastapi_host: str = Field("0.0.0.0", alias="API_HOST")
    fastapi_port: int = Field(8000, alias="API_PORT")
    fastapi_env: str = Field("development", alias="APP_ENV")
    
    # Hybrid Search
    hybrid_rrf_k: int = Field(60, alias="RRF_K")
    hybrid_default_vector_weight: float = Field(0.5, alias="VECTOR_WEIGHT")
    hybrid_default_bm25_weight: float = Field(0.5, alias="BM25_WEIGHT")
    hybrid_default_top_k: int = Field(10, alias="HYBRID_SEARCH_TOP_K")
    
    # MongoDB Atlas Search Index Names
    bm25_index_name: str = Field("bm25_english", alias="BM25_INDEX_NAME")
    vector_index_name: str = Field("vector_index_english", alias="VECTOR_INDEX_NAME")
    
    # Logging
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    
    # JWT Authentication
    jwt_secret_key: str = Field("examsmith-secret-key-change-in-production", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(1440, alias="JWT_EXPIRE_MINUTES")
    
    # ExamSmith Application Database
    mongodb_users_db: str = Field("examsmith", alias="MONGODB_USERS_DB")
    
    # Pipeline Database (Instructor approved papers for students)
    mongodb_pipeline_db: str = Field("10_english", alias="MONGODB_PIPELINE_DB")
    mongodb_pipeline_collection: str = Field("generatedQuestionPapers", alias="MONGODB_PIPELINE_COLLECTION")
    
    # Student Attempts & Evaluations
    mongodb_attempts_collection: str = Field("student_attempts", alias="MONGODB_ATTEMPTS_COLLECTION")
    mongodb_evaluations_collection: str = Field("evaluations", alias="MONGODB_EVALUATIONS_COLLECTION")
    
    class Config:
        env_file = str(env_file_path) if env_file_path.exists() else ".env"
        extra = "allow"

settings = Settings()
