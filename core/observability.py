import os
import json
from datetime import datetime
from collections import defaultdict

class StructuredLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.in_memory_logs = []
        
        # Summary accumulators
        self.total_items = 0
        self.themes_found = 0
        self.themes_rejected = 0
        self.confidence_sum = 0.0
        self.confidence_count = 0
        self.total_latency_ms = 0.0
        
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            self.disk_available = True
        except Exception as e:
            print(f"Warning: Disk write failed, falling back to in-memory logs. {e}")
            self.disk_available = False

    def log_event(self, agent: str, task_type: str, status: str, latency_ms: float, token_count: int, notes: str):
        """
        Log an event either to disk or in memory gracefully.
        """
        date_str = datetime.utcnow().strftime("%Y%m%d")
        log_file = os.path.join(self.log_dir, f"run_{date_str}.jsonl")
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "task_type": task_type,
            "status": status,
            "latency_ms": latency_ms,
            "token_count": token_count,
            "notes": notes
        }
        
        self.total_latency_ms += latency_ms
        
        # Simple extraction for summary metrics based on specific notes or task types.
        # This relies on the agent passing formatted notes or updating explicitly.
        # In this implementation, the main agent will explicitly update summary stats if needed.
        
        if self.disk_available:
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(event) + "\n")
            except Exception as e:
                self.disk_available = False
                self.in_memory_logs.append(event)
        else:
            self.in_memory_logs.append(event)

    def update_summary(self, total_items=0, themes_found=0, themes_rejected=0, confidence_sum=0.0, confidence_count=0):
        """Explicitly update summary metrics from the evaluator/planner."""
        self.total_items += total_items
        self.themes_found += themes_found
        self.themes_rejected += themes_rejected
        self.confidence_sum += confidence_sum
        self.confidence_count += confidence_count

    def get_run_summary(self) -> dict:
        """
        Return the summary of the run.
        """
        avg_confidence = (self.confidence_sum / self.confidence_count) if self.confidence_count > 0 else 0.0
        
        return {
            "total_items": self.total_items,
            "themes_found": self.themes_found,
            "themes_rejected": self.themes_rejected,
            "avg_confidence": round(avg_confidence, 3),
            "total_latency_ms": round(self.total_latency_ms, 2)
        }
