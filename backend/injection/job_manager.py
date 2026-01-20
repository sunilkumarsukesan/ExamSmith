import uuid
from datetime import datetime
from typing import Dict, Any
from src.models import JobStatus
import logging

logger = logging.getLogger(__name__)

class JobManager:
    """Manages ingestion jobs and their progress (SUGGESTION)"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
    
    def create_job(self) -> str:
        """Create a new ingestion job"""
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "status": JobStatus.PENDING,
            "total_records": 0,
            "processed_records": 0,
            "failed_records": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        logger.info(f"Job created: {job_id}")
        return job_id
    
    def update_job_status(self, job_id: str, status: JobStatus):
        """Update job status"""
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            self.jobs[job_id]["updated_at"] = datetime.utcnow()
            logger.info(f"Job {job_id} status: {status}")
    
    def update_job_progress(self, job_id: str, processed: int, failed: int, total: int):
        """Update job progress (SUGGESTION)"""
        if job_id in self.jobs:
            self.jobs[job_id]["processed_records"] = processed
            self.jobs[job_id]["failed_records"] = failed
            self.jobs[job_id]["total_records"] = total
            self.jobs[job_id]["updated_at"] = datetime.utcnow()
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status and progress"""
        return self.jobs.get(job_id)
    
    def calculate_progress_percent(self, job_id: str) -> float:
        """Calculate progress percentage (SUGGESTION)"""
        if job_id not in self.jobs:
            return 0.0
        job = self.jobs[job_id]
        total = job["total_records"]
        if total == 0:
            return 0.0
        return (job["processed_records"] / total) * 100
