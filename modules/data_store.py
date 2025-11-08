"""
Data Store Module
Handles storage and retrieval of metrics data
"""

import json
import os
from datetime import datetime
from collections import deque


class DataStore:
    """Stores metrics data with optional persistence"""
    
    def __init__(self, persist_to_file=True, max_memory_items=1000):
        self.persist_to_file = persist_to_file
        self.max_memory_items = max_memory_items
        self.data_file = os.getenv('METRICS_DATA_FILE', 'data/metrics.jsonl')
        
        # In-memory storage (ring buffer)
        self.memory_store = deque(maxlen=max_memory_items)
        
        # Ensure data directory exists
        if self.persist_to_file:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def store(self, metrics):
        """Store metrics data"""
        # Add to memory
        self.memory_store.append(metrics)
        
        # Persist to file if enabled
        if self.persist_to_file:
            self._persist_to_file(metrics)
    
    def _persist_to_file(self, metrics):
        """Persist metrics to file (JSONL format)"""
        try:
            with open(self.data_file, 'a') as f:
                json.dump(metrics, f)
                f.write('\n')
        except Exception as e:
            print(f"Error persisting metrics to file: {e}")
    
    def get_history(self, limit=100):
        """Get historical metrics from memory"""
        # Return most recent items
        items = list(self.memory_store)
        return items[-limit:] if len(items) > limit else items
    
    def get_latest(self):
        """Get the most recent metrics"""
        if self.memory_store:
            return self.memory_store[-1]
        return None
    
    def load_from_file(self, limit=None):
        """Load metrics from file"""
        if not os.path.exists(self.data_file):
            return []
        
        metrics = []
        try:
            with open(self.data_file, 'r') as f:
                for line in f:
                    if line.strip():
                        metrics.append(json.loads(line))
            
            # Return most recent items
            if limit:
                return metrics[-limit:]
            return metrics
        except Exception as e:
            print(f"Error loading metrics from file: {e}")
            return []
    
    def clear_old_data(self, days=7):
        """Clear data older than specified days"""
        if not os.path.exists(self.data_file):
            return
        
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            temp_file = self.data_file + '.tmp'
            
            with open(self.data_file, 'r') as infile, open(temp_file, 'w') as outfile:
                for line in infile:
                    if line.strip():
                        data = json.loads(line)
                        if 'timestamp' in data:
                            timestamp = datetime.fromisoformat(data['timestamp']).timestamp()
                            if timestamp >= cutoff_time:
                                outfile.write(line)
            
            # Replace old file with cleaned file
            os.replace(temp_file, self.data_file)
            print(f"Cleared metrics data older than {days} days")
        except Exception as e:
            print(f"Error clearing old data: {e}")
    
    def get_stats(self):
        """Get statistics about stored data"""
        return {
            'memory_items': len(self.memory_store),
            'max_memory_items': self.max_memory_items,
            'persist_enabled': self.persist_to_file,
            'data_file': self.data_file if self.persist_to_file else None
        }
