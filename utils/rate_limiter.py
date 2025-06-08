import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter with adaptive delays"""
    
    def __init__(self):
        self.requests_per_minute = 30
        self.delay_between_requests = 2.0
        self.last_request_time = defaultdict(float)
        self.request_history = defaultdict(deque)
        self.adaptive_delays = defaultdict(float)
        
    async def wait_if_needed(self, source: str = "default") -> None:
        """Apply rate limiting with adaptive delay"""
        current_time = time.time()
        
        # Update request history
        history = self.request_history[source]
        history.append(current_time)
        
        # Clear old history
        while history and history[0] < current_time - 60:
            history.popleft()
        
        # Check rate limits
        if len(history) >= self.requests_per_minute:
            wait_time = 60 - (current_time - history[0])
            if wait_time > 0:
                logger.info(f"Rate limit reached for {source}, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        # Apply adaptive delay
        last_time = self.last_request_time[source]
        adaptive_delay = self.adaptive_delays.get(source, self.delay_between_requests)
        
        time_since_last = current_time - last_time
        if time_since_last < adaptive_delay:
            await asyncio.sleep(adaptive_delay - time_since_last)
        
        self.last_request_time[source] = time.time()
