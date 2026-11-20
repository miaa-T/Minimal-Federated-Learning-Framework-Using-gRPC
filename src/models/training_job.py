from dataclasses import dataclass, field
from enum import Enum

from .training_result import TrainingResult
from .training_task import TrainingTask


class TrainingJobStatus(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class TrainingJob:
    job_id: str
    expression: str
    status: TrainingJobStatus = TrainingJobStatus.CREATED
    tasks: list[TrainingTask] = field(default_factory=list)
    results: dict[str, TrainingResult] = field(default_factory=dict)
    final_result: int | float | None = None
