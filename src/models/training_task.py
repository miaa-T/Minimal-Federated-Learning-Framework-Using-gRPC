from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingTask:
    task_id: str
    job_id: str
    expression: str
    position: int
    sign: int = 1
    participant_id: str | None = None
