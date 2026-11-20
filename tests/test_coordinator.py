import pytest

from src.coordinator.coordinator import Coordinator
from src.models.training_job import TrainingJobStatus
from src.models.training_result import TrainingResult
from src.participant.participant_service import Participant


def configured_coordinator() -> Coordinator:
    coordinator = Coordinator()
    coordinator.register_participant(Participant("A"))
    coordinator.register_participant(Participant("B"))
    return coordinator


def test_complete_federated_computation():
    coordinator = configured_coordinator()
    job = coordinator.start_training(
        "JOB_001", "(12 * 5) + (30 / 6) - (8 * 4) + (15 + 7)"
    )
    coordinator.create_tasks(job.job_id)
    tasks = coordinator.distribute_tasks(job.job_id)
    for task in tasks:
        participant = coordinator._participants[task.participant_id]
        coordinator.collect_result(participant.execute_task(task))
    assert coordinator.aggregate_results(job.job_id) == 55
    assert coordinator.get_training_status(job.job_id).status == TrainingJobStatus.COMPLETED


def test_registration_and_result_validation():
    coordinator = Coordinator()
    coordinator.register_participant(Participant("A"))
    with pytest.raises(ValueError, match="already registered"):
        coordinator.register_participant(Participant("A"))

    job = coordinator.start_training("JOB_1", "2 + 3")
    coordinator.create_tasks(job.job_id)
    task = coordinator.distribute_tasks(job.job_id)[0]
    with pytest.raises(ValueError, match="Unknown participant"):
        coordinator.collect_result(TrainingResult("B", task.task_id, 2))
    with pytest.raises(ValueError, match="Unknown task"):
        coordinator.collect_result(TrainingResult("A", "UNKNOWN", 2))


def test_duplicate_result_and_missing_participants():
    coordinator = configured_coordinator()
    job = coordinator.start_training("JOB_1", "2 + 3")
    coordinator.create_tasks(job.job_id)
    task = coordinator.distribute_tasks(job.job_id)[0]
    result = coordinator._participants[task.participant_id].execute_task(task)
    coordinator.collect_result(result)
    with pytest.raises(ValueError, match="already been submitted"):
        coordinator.collect_result(result)

    empty = Coordinator()
    with pytest.raises(ValueError, match="At least one participant"):
        empty.start_training("JOB_2", "1 + 1")
