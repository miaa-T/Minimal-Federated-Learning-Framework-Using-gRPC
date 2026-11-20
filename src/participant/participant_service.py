from src.computation.expression_engine import ExpressionEngine
from src.models.participant import ParticipantInfo, ParticipantStatus
from src.models.training_result import TrainingResult
from src.models.training_task import TrainingTask


class Participant:
    def __init__(self, participant_id: str, engine: ExpressionEngine | None = None):
        if not participant_id:
            raise ValueError("Participant ID must not be empty")
        self.info = ParticipantInfo(participant_id)
        self._engine = engine or ExpressionEngine()

    @property
    def participant_id(self) -> str:
        return self.info.participant_id

    @property
    def status(self) -> ParticipantStatus:
        return self.info.status

    def execute_task(self, task: TrainingTask) -> TrainingResult:
        if task.participant_id != self.participant_id:
            raise ValueError(
                f"Task {task.task_id} is not assigned to participant {self.participant_id}"
            )
        self.info.status = ParticipantStatus.BUSY
        try:
            local_result = self._engine.evaluate(task.expression)
            return TrainingResult(self.participant_id, task.task_id, local_result)
        finally:
            self.info.status = ParticipantStatus.IDLE
