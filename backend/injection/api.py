from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import logging
import json
from src.models import InputDocument, IngestJobResponse, JobStatusResponse, JobStatus
from src.ingest_service import IngestionService
from src.job_manager import JobManager
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

job_manager = JobManager()
ingestion_service = IngestionService(job_manager)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@router.post("/ingest/file", response_model=IngestJobResponse)
async def ingest_file(file: UploadFile = File(...)):
    """
    Ingest JSON documents from file upload.
    
    Args:
        file: JSON file containing array of documents
        
    Returns:
        Job creation response with job_id
    """
    try:
        # Read file content
        content = await file.read()
        
        # Parse JSON
        try:
            documents = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        if not isinstance(documents, list):
            raise HTTPException(status_code=400, detail="JSON must be an array of documents")
        
        if not documents:
            raise HTTPException(status_code=400, detail="No documents provided in file")
        
        # Validate each document
        validated_docs = []
        errors = []
        for idx, doc in enumerate(documents):
            try:
                validated_docs.append(InputDocument(**doc))
            except Exception as e:
                error_msg = f"Document {idx}: {str(e)}"
                errors.append(error_msg)
                logger.warning(f"⚠️  {error_msg}")
        
        if errors:
            error_details = "\n".join(errors[:3])  # Show first 3 errors
            logger.error(f"❌ {len(errors)} document(s) failed validation")
            raise HTTPException(
                status_code=422, 
                detail=f"{len(errors)} document(s) failed validation.\n{error_details}"
            )
        
        if not validated_docs:
            raise HTTPException(status_code=400, detail="No valid documents after validation")
        
        job_id = job_manager.create_job()
        logger.info(f"📥 File upload received - {len(validated_docs)} documents - File: {file.filename} - Job ID: {job_id}")
        print(f"\n📥 File upload received: {file.filename} ({len(validated_docs)} documents)")
        
        # Run ingestion in background
        asyncio.create_task(
            ingestion_service.ingest_json_documents(
                [doc.dict() for doc in validated_docs],
                job_id
            )
        )
        
        job = job_manager.get_job_status(job_id)
        print(f"✓ Job queued. Check progress with: GET /ingest/status/{job_id}\n")
        
        return IngestJobResponse(
            job_id=job_id,
            status=job["status"],
            created_at=job["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ File upload endpoint error: {str(e)}")
        print(f"❌ Error: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest/json", response_model=IngestJobResponse)
async def ingest_json(documents: List[InputDocument]):
    """
    Ingest JSON documents into MongoDB.
    
    Args:
        documents: List of input documents
        
    Returns:
        Job creation response with job_id
    """
    try:
        if not documents:
            raise HTTPException(status_code=400, detail="No documents provided")
        
        job_id = job_manager.create_job()
        logger.info(f"📥 Ingestion request received - {len(documents)} documents - Job ID: {job_id}")
        print(f"\n📥 Ingestion request received: {len(documents)} documents")
        
        # Run ingestion in background
        asyncio.create_task(
            ingestion_service.ingest_json_documents(
                [doc.dict() for doc in documents],
                job_id
            )
        )
        
        job = job_manager.get_job_status(job_id)
        print(f"✓ Job queued. Check progress with: GET /ingest/status/{job_id}\n")
        
        return IngestJobResponse(
            job_id=job_id,
            status=job["status"],
            created_at=job["created_at"]
        )
    except Exception as e:
        logger.error(f"❌ Ingestion endpoint error: {str(e)}")
        print(f"❌ Error: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ingest/status/{job_id}", response_model=JobStatusResponse)
async def get_ingestion_status(job_id: str):
    """
    Get ingestion job status and progress (SUGGESTION).
    
    Args:
        job_id: Job ID
        
    Returns:
        Job status with progress information
    """
    job = job_manager.get_job_status(job_id)
    
    if not job:
        logger.warning(f"Status check for unknown job: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")
    
    progress_percent = job_manager.calculate_progress_percent(job_id)
    
    logger.debug(f"Status check - Job {job_id}: {job['status'].value} ({progress_percent:.1f}%)")
    
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        total_records=job["total_records"],
        processed_records=job["processed_records"],
        failed_records=job["failed_records"],
        progress_percent=progress_percent,
        created_at=job["created_at"],
        updated_at=job["updated_at"]
    )
