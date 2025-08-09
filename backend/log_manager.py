"""
Log management system for the quant trading platform
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
from collections import deque
import threading
import queue

class LogHandler(logging.Handler):
    """Custom log handler that stores logs in memory and broadcasts to subscribers"""
    
    def __init__(self):
        super().__init__()
        self.log_queue = deque(maxlen=1000)  # Store last 1000 log entries
        self.subscribers = set()
        self.lock = threading.Lock()
        
    def emit(self, record):
        """Emit a log record"""
        try:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': self.format(record),
                'module': getattr(record, 'module', 'unknown'),
                'function': getattr(record, 'funcName', 'unknown'),
                'line': getattr(record, 'lineno', 0)
            }
            
            with self.lock:
                self.log_queue.append(log_entry)
                
                # Notify subscribers
                for subscriber_queue in list(self.subscribers):
                    try:
                        subscriber_queue.put_nowait(log_entry)
                    except queue.Full:
                        # Remove full queues to prevent memory leaks
                        self.subscribers.discard(subscriber_queue)
                        
        except Exception:
            # Don't let log handler failures break the application
            pass
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent log entries"""
        with self.lock:
            return list(self.log_queue)[-limit:]
    
    def subscribe(self) -> queue.Queue:
        """Subscribe to real-time log updates"""
        subscriber_queue = queue.Queue(maxsize=100)
        with self.lock:
            self.subscribers.add(subscriber_queue)
        return subscriber_queue
    
    def unsubscribe(self, subscriber_queue: queue.Queue):
        """Unsubscribe from log updates"""
        with self.lock:
            self.subscribers.discard(subscriber_queue)

class LogManager:
    """Central log management for the application"""
    
    def __init__(self):
        self.handler = LogHandler()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.handler.setFormatter(formatter)
        
        # Add handler to relevant loggers (avoid uvicorn loggers to prevent startup conflicts)
        loggers_to_capture = [
            'data_fetcher',
            'proxy_detector', 
            'api.main',
            'backtest_engine',
            'screeners',
            'screener_backtest_integration',
            'backtrader_wrapper',
            '__main__'
        ]
        
        for logger_name in loggers_to_capture:
            logger = logging.getLogger(logger_name)
            logger.addHandler(self.handler)
            logger.setLevel(logging.INFO)
        
        # Also capture root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.handler)
        
    def get_recent_logs(self, limit: int = 100, level: Optional[str] = None) -> List[Dict]:
        """Get recent logs, optionally filtered by level"""
        logs = self.handler.get_recent_logs(limit)
        
        if level:
            logs = [log for log in logs if log['level'] == level.upper()]
            
        return logs
    
    def get_log_stats(self) -> Dict:
        """Get log statistics"""
        logs = self.handler.get_recent_logs(1000)
        
        level_counts = {}
        for log in logs:
            level = log['level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        recent_errors = [log for log in logs if log['level'] in ['ERROR', 'CRITICAL']]
        
        return {
            'total_logs': len(logs),
            'level_counts': level_counts,
            'recent_errors': recent_errors[-10:],  # Last 10 errors
            'last_update': datetime.now().isoformat()
        }
    
    def subscribe_to_logs(self) -> queue.Queue:
        """Subscribe to real-time log updates"""
        return self.handler.subscribe()
    
    def unsubscribe_from_logs(self, subscriber_queue: queue.Queue):
        """Unsubscribe from log updates"""
        self.handler.unsubscribe(subscriber_queue)

# Global log manager instance
log_manager = LogManager()