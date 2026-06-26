import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class A2AMessage:
    """Agent-to-Agent communication message."""
    sender: str
    recipient: str
    task_type: str
    payload: dict
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "PENDING"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class MessageBus:
    """Central bus for managing A2AMessage routing."""

    def __init__(self):
        # Queues indexed by recipient name
        self.queues: dict[str, list[A2AMessage]] = defaultdict(list)
        # Global store of all messages by ID for easy lookup
        self.message_store: dict[str, A2AMessage] = {}

    def send(self, message: A2AMessage) -> None:
        """Send a message to the recipient's queue."""
        self.queues[message.recipient].append(message)
        self.message_store[message.msg_id] = message

    def receive(self, agent_name: str) -> Optional[A2AMessage]:
        """Receive the next pending message for an agent."""
        if self.queues[agent_name]:
            # FIFO pop
            return self.queues[agent_name].pop(0)
        return None

    def wait_for_all(self, task_ids: list[str], timeout: int = 10) -> list[A2AMessage]:
        """
        Wait until all messages with the given task_ids reach a terminal state.
        In this simulated environment, tasks are processed synchronously before
        wait_for_all is called, but this supports an async pattern.
        """
        start_time = time.time()
        completed_messages = []

        while time.time() - start_time < timeout:
            all_done = True
            current_completed = []
            
            for tid in task_ids:
                msg = self.message_store.get(tid)
                if msg and msg.status in ("DONE", "FAILED"):
                    current_completed.append(msg)
                else:
                    all_done = False
                    
            if all_done:
                return current_completed
            
            time.sleep(0.1)

        # Return whatever we have on timeout
        return [self.message_store.get(tid) for tid in task_ids if self.message_store.get(tid)]
