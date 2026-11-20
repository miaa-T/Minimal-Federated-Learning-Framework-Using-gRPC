from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingResult:
    participant_id: str
    task_id: str
    local_result: int | float
