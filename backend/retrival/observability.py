import logging
import time
from functools import wraps
from typing import Callable, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("retrival")

class RetrievalMetrics:
    """Track retrieval performance metrics."""
    
    def __init__(self):
        self.retrieval_latency = {}  # {mode: [latencies]}
        self.tokens_used = {}        # {mode: total_tokens}
        self.search_counts = {}      # {mode: count}
        self.errors = {}             # {mode: error_count}
    
    def record_retrieval(self, mode: str, latency_ms: float, tokens: int = 0, error: bool = False):
        """Record a retrieval operation."""
        if mode not in self.retrieval_latency:
            self.retrieval_latency[mode] = []
            self.tokens_used[mode] = 0
            self.search_counts[mode] = 0
            self.errors[mode] = 0
        
        self.retrieval_latency[mode].append(latency_ms)
        self.tokens_used[mode] += tokens
        self.search_counts[mode] += 1
        if error:
            self.errors[mode] += 1
        
        logger.info(
            f"retrieval.{mode}",
            extra={
                "latency_ms": latency_ms,
                "tokens": tokens,
                "mode": mode,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def get_stats(self, mode: str = None) -> dict:
        """Get aggregated stats."""
        if mode:
            latencies = self.retrieval_latency.get(mode, [])
            if not latencies:
                return {"mode": mode, "status": "no_data"}
            return {
                "mode": mode,
                "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
                "max_latency_ms": max(latencies),
                "min_latency_ms": min(latencies),
                "total_searches": self.search_counts[mode],
                "total_tokens": self.tokens_used[mode],
                "errors": self.errors[mode],
                "error_rate": round(self.errors[mode] / self.search_counts[mode] * 100, 2) if self.search_counts[mode] > 0 else 0,
            }
        
        return {m: self.get_stats(m) for m in self.retrieval_latency.keys()}

def track_retrieval(mode: str):
    """Decorator to track retrieval latency and errors."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start = time.time()
            error = False
            try:
                result = await func(*args, **kwargs)
                latency_ms = (time.time() - start) * 1000
                metrics.record_retrieval(mode, latency_ms, error=False)
                logger.debug(f"{mode} retrieval took {latency_ms:.2f}ms")
                return result
            except Exception as e:
                latency_ms = (time.time() - start) * 1000
                metrics.record_retrieval(mode, latency_ms, error=True)
                logger.error(f"{mode} retrieval failed after {latency_ms:.2f}ms: {str(e)}")
                raise
        return async_wrapper
    return decorator

# Global metrics instance
metrics = RetrievalMetrics()
