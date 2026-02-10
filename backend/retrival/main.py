from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
import asyncio
import traceback
from observability import logger
from mongo.client import mongo_client
from api import router as retrieval_router

# Import new role-based routers
from routes.auth_routes import router as auth_router
from routes.admin_routes import router as admin_router
from routes.instructor_routes import router as instructor_router
from routes.student_routes import router as student_router
from routes.pdf_routes import router as pdf_router
from routes.evaluation_routes import router as evaluation_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# Suppress asyncio connection reset errors on Windows
if sys.platform == 'win32':
    # Use WindowsSelectorEventLoopPolicy to avoid ProactorEventLoop issues
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 ExamSmith Retrieval Backend starting...")
    yield
    logger.info("🛑 Shutting down...")
    mongo_client.close()

# Create FastAPI app
app = FastAPI(
    title="ExamSmith Retrieval API",
    description="AI-powered retrieval and answer evaluation for TN SSLC English",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "*"  # Allow all origins in development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
# Existing retrieval routes (unchanged)
app.include_router(retrieval_router, prefix="/api/v1", tags=["retrieval"])

# New role-based routes
app.include_router(auth_router, prefix="/api/v1", tags=["authentication"])
app.include_router(admin_router, prefix="/api/v1", tags=["admin"])
app.include_router(instructor_router, prefix="/api/v1", tags=["instructor"])
app.include_router(student_router, prefix="/api/v1", tags=["student"])
app.include_router(pdf_router, prefix="/api/v1", tags=["pdf"])
app.include_router(evaluation_router, prefix="/api/v1", tags=["evaluation"])

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mongodb": "connected" if mongo_client.client is not None else "disconnected",
        "service": "ExamSmith Retrieval Backend",
        "cors_enabled": True,
        "endpoints": {
            "chat_quota": "/api/v1/student/chat/quota",
            "chat_stream": "/api/v1/student/chat/stream",
            "api_docs": "/docs"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {''.join(traceback.format_tb(exc.__traceback__))}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    uvicorn.run(
        app,
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        log_level=settings.log_level.lower(),
        timeout_keep_alive=300,  # 5 minutes timeout
    )
