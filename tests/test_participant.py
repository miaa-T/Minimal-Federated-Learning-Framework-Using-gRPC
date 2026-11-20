from src.models.participant import ParticipantStatus
from src.models.training_task import TrainingTask
from src.models.training_result import TrainingResult
from src.participant.participant_service import Participant


def test_participant_executes_task_and_returns_to_idle():
    participant = Participant("A")
    task = TrainingTask("TASK_1", "JOB_1", "12 * 5", 1, participant_id="A")
    result = participant.execute_task(task)
    assert result == TrainingResult("A", "TASK_1", 60)
    assert participant.status == ParticipantStatus.IDLE
