import requests
import asyncio
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from src.config import (
    MISTRAL_API_KEY, 
    MISTRAL_EMBEDDING_MODEL, 
    MISTRAL_EMBEDDING_DIM,
    EMBEDDING_TIMEOUT,
    MAX_EMBEDDING_RETRIES,
    RETRY_BACKOFF_FACTOR
)

logger = logging.getLogger(__name__)

class EmbeddingValidator:
    """Validates embedding vectors (SUGGESTION)"""
    
    @staticmethod
    def validate_embedding(embedding: List[float], expected_dim: int = MISTRAL_EMBEDDING_DIM) -> bool:
        """Validate embedding dimension and content"""
        if not embedding or len(embedding) != expected_dim:
            return False
        return all(isinstance(x, (int, float)) for x in embedding)

class Embedder:
    """Handles embedding generation using Mistral API"""
    
    def __init__(self):
        self.api_key = MISTRAL_API_KEY
        self.model = MISTRAL_EMBEDDING_MODEL
        self.expected_dim = MISTRAL_EMBEDDING_DIM
        self.timeout = EMBEDDING_TIMEOUT
        self.max_retries = MAX_EMBEDDING_RETRIES
        self.base_url = "https://api.mistral.ai/v1/embeddings"
    
    @retry(
        stop=stop_after_attempt(MAX_EMBEDDING_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of texts using Mistral API with retry logic.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            Exception: If embedding fails after max retries
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "input": texts
            }
            
            logger.info(f"🧠 Embedding batch of {len(texts)} texts...")
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            embeddings = [item['embedding'] for item in result['data']]
            
            # Validate embeddings (SUGGESTION)
            for emb in embeddings:
                if not EmbeddingValidator.validate_embedding(emb):
                    raise ValueError(f"Invalid embedding dimension: {len(emb)}")
            
            logger.info(f"✅ Successfully embedded {len(embeddings)} texts")
            return embeddings
            
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Embedding request timeout after {self.timeout}s")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Embedding request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Embedding processing failed: {str(e)}")
            raise
    
    async def embed_documents(self, documents: List[Dict[str, Any]], batch_size: int) -> List[Dict[str, Any]]:
        """
        Embed all documents in batches (SUGGESTION: handle partial batch failures).
        
        Args:
            documents: List of documents to embed
            batch_size: Number of documents per batch
            
        Returns:
            Documents with embeddings added
        """
        failed_docs = []
        total_batches = (len(documents) + batch_size - 1) // batch_size
        embedded_count = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            pending = total_batches - batch_num
            contents = [doc['content'] for doc in batch]
            
            try:
                progress_bar = "█" * batch_num + "░" * pending
                logger.info(f"🧠 EMBEDDING [Batch {batch_num}/{total_batches}] [{progress_bar}] ⏳ {len(batch)} pending")
                print(f"   Batch {batch_num}/{total_batches} - Processing {len(batch)} documents...", end=" ", flush=True)
                
                embeddings = await self.embed_batch(contents)
                for doc, embedding in zip(batch, embeddings):
                    doc['embedding'] = embedding
                
                embedded_count += len(embeddings)
                logger.info(f"✅ BATCH SUCCESS [Batch {batch_num}/{total_batches}] 📊 {embedded_count}/{len(documents)} completed | ⏳ {len(documents) - embedded_count} pending")
                print(f"✓")
                
            except Exception as e:
                logger.error(f"❌ BATCH FAILED [Batch {batch_num}/{total_batches}] {str(e)[:60]}")
                print(f"✗ Failed: {str(e)[:50]}")
                failed_docs.extend(batch)
        
        if failed_docs:
            logger.warning(f"⚠️  EMBEDDING SUMMARY - {len(failed_docs)}/{len(documents)} documents failed | ✅ {embedded_count} succeeded")
        else:
            logger.info(f"🎉 EMBEDDING COMPLETE - All {len(documents)} documents embedded successfully!")
        
        return documents, failed_docs
