from abc import ABC, abstractmethod
from typing import List
from models import Citation

class RetrieverMode(ABC):
    """Abstract base class for retrieval strategies."""
    
    @abstractmethod
    async def retrieve(self, query: str, **kwargs) -> tuple[List[dict], List[Citation]]:
        """
        Retrieve relevant documents for the given query.
        
        Returns:
            (context_blocks, citations)
        """
        pass
