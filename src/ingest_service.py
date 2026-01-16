import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from tqdm import tqdm
from src.mongo_client import MongoDBClient
from src.embedder import Embedder
from src.deduplicator import Deduplicator
from src.job_manager import JobManager
from src.models import JobStatus
from src.config import FAILED_RECORDS_PATH, BATCH_SIZE

logger = logging.getLogger(__name__)

class IngestionService:
    """Main ingestion pipeline service"""
    
    def __init__(self, job_manager: JobManager):
        self.mongo_client = MongoDBClient()
        self.embedder = Embedder()
        self.job_manager = job_manager
        self.failed_records_path = FAILED_RECORDS_PATH
    
    async def ingest_json_documents(self, documents: List[Dict[str, Any]], job_id: str):
        """
        Main ingestion flow with progress tracking.
        
        Args:
            documents: List of documents to ingest
            job_id: Job ID for progress tracking
        """
        try:
            self.job_manager.update_job_status(job_id, JobStatus.PROCESSING)
            self.mongo_client.connect()
            
            total = len(documents)
            self.job_manager.update_job_progress(job_id, 0, 0, total)
            
            # Console header
            print("\n" + "="*70)
            print(f"🚀 INGESTION PIPELINE STARTED - Job ID: {job_id}")
            print(f"📊 Total documents to process: {total}")
            print("="*70 + "\n")
            
            # Step 1: Deduplicate
            print(f"[STEP 1/6] 🔍 Deduplicating {total} documents...")
            logger.info(f"[Job {job_id}] Step 1: Deduplicating {total} documents...")
            documents = Deduplicator.add_hash_to_documents(documents)
            print(f"✓ Deduplication complete")
            
            # Step 2: Embed documents
            print(f"\n[STEP 2/6] 🧠 Embedding documents in batches of {BATCH_SIZE}...")
            logger.info(f"[Job {job_id}] 🧠 Step 2: Starting embedding of {total} documents in batches of {BATCH_SIZE}...")
            documents, failed_embedding = await self.embedder.embed_documents(documents, BATCH_SIZE)
            success_embed = len(documents) - len(failed_embedding)
            print(f"✓ Embedding complete: {success_embed} succeeded, {len(failed_embedding)} failed")
            logger.info(f"[Job {job_id}] 🎉 Embedding Step Complete: ✅ {success_embed} succeeded | ❌ {len(failed_embedding)} failed")
            
            # Step 3: Prepare documents for MongoDB
            print(f"\n[STEP 3/6] 📝 Preparing documents for MongoDB...")
            logger.info(f"[Job {job_id}] Step 3: Preparing documents...")
            for doc in documents:
                doc['created_at'] = datetime.utcnow()
                doc['updated_at'] = datetime.utcnow()
            print(f"✓ {len(documents)} documents prepared")
            
            # Step 4: Upsert to MongoDB
            print(f"\n[STEP 4/6] 💾 Upserting to MongoDB...")
            logger.info(f"[Job {job_id}] 💾 Step 4: Starting MongoDB injection...")
            result = self.mongo_client.upsert_documents(documents)
            print(f"✓ MongoDB upsert complete: {result.get('matched', 0)} matched, {result.get('upserted', 0)} upserted")
            logger.info(f"[Job {job_id}] ✅ MongoDB Injection Complete: New: {result.get('upserted', 0)} | Updated: {result.get('matched', 0)}")
            
            # Step 5: Handle failures
            if failed_embedding:
                print(f"\n[STEP 5/6] ⚠️  Logging {len(failed_embedding)} failed records...")
                logger.warning(f"[Job {job_id}] Logging {len(failed_embedding)} failed records...")
                self._log_failed_records(failed_embedding)
                print(f"✓ Failed records saved to {FAILED_RECORDS_PATH}")
            else:
                print(f"\n[STEP 5/6] ⚠️  No failures to log")
            
            processed = len(documents) - len(failed_embedding)
            failed = len(failed_embedding)
            
            self.job_manager.update_job_progress(job_id, processed, failed, total)
            
            # Step 6: Complete
            status = JobStatus.COMPLETED if failed == 0 else JobStatus.PARTIAL_FAILURE
            self.job_manager.update_job_status(job_id, status)
            
            # Final summary
            print(f"\n[STEP 6/6] ✅ Pipeline Complete")
            print("\n" + "="*70)
            print(f"📈 FINAL RESULTS")
            print(f"   Total:      {total}")
            print(f"   Processed:  {processed} ({(processed/total*100):.1f}%)")
            print(f"   Failed:     {failed} ({(failed/total*100):.1f}%)")
            print(f"   Status:     {status.value.upper()}")
            print(f"   Job ID:     {job_id}")
            print("="*70 + "\n")
            
            logger.info(f"[Job {job_id}] Ingestion complete. Processed: {processed}, Failed: {failed}")
            
        except Exception as e:
            print(f"\n❌ INGESTION FAILED")
            print(f"   Error: {str(e)}")
            print(f"   Job ID: {job_id}\n")
            logger.error(f"[Job {job_id}] Ingestion failed: {str(e)}")
            self.job_manager.update_job_status(job_id, JobStatus.FAILED)
        finally:
            self.mongo_client.disconnect()
    
    def _log_failed_records(self, records: List[Dict[str, Any]]):
        """Append failed records to JSON file (SUGGESTION: robust error logging)"""
        try:
            existing_failures = []
            try:
                with open(self.failed_records_path, 'r') as f:
                    existing_failures = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            
            existing_failures.extend(records)
            
            with open(self.failed_records_path, 'w') as f:
                json.dump(existing_failures, f, indent=2, default=str)
            
            logger.info(f"Logged {len(records)} failed records")
        except Exception as e:
            logger.error(f"Failed to log records: {str(e)}")
