import json
import os
from typing import Any, Optional

class SessionMemory:
    """In-memory store for session-specific data."""

    def __init__(self):
        self.store: dict[str, dict[str, Any]] = {}

    def save(self, session_id: str, key: str, value: Any) -> None:
        """Save a value to the session store."""
        if session_id not in self.store:
            self.store[session_id] = {}
        self.store[session_id][key] = value

    def get(self, session_id: str, key: str) -> Optional[Any]:
        """Retrieve a value from the session store."""
        return self.store.get(session_id, {}).get(key)

    def clear(self, session_id: str) -> None:
        """Clear all data for a specific session."""
        if session_id in self.store:
            del self.store[session_id]


class EpisodicMemory:
    """Persistent storage for episodic logs (runs)."""

    def __init__(self, log_path: str = "logs/episodic_log.jsonl"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def append_run(self, run_data: dict) -> None:
        """Append a run dictionary as a JSON line to the log."""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(run_data) + "\n")
        except IOError as e:
            print(f"Failed to write episodic log: {e}")

    def get_last_n_runs(self, n: int) -> list[dict]:
        """Retrieve the last N runs from the log."""
        if not os.path.exists(self.log_path):
            return []

        runs = []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        runs.append(json.loads(line))
        except IOError as e:
            print(f"Failed to read episodic log: {e}")

        return runs[-n:] if n > 0 else runs
