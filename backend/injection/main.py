from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from src.api import router
from src.config import LOG_LEVEL, LOG_FILE_PATH, API_HOST, API_PORT

# Create logs directory if not exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

# Configure logging with UTF-8 support for Windows
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="ExamSmith Ingestion Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("ExamSmith Ingestion Service starting...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("ExamSmith Ingestion Service shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
