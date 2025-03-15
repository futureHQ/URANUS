from enum import Enum


class AgentState(str, Enum):
    """Possible states of an agent."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"
    ERROR = "error"