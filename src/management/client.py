from src.coordinator.coordinator import Coordinator
from src.participant.participant_service import Participant


def run_demo() -> None:
    coordinator = Coordinator()
    for participant_id in ("A", "B"):
        coordinator.register_participant(Participant(participant_id))
        print(f"[Coordinator] Participant {participant_id} registered")

    expression = "(12 * 5) + (30 / 6) - (8 * 4) + (15 + 7)"
    job = coordinator.start_training("JOB_001", expression)
    print(f"[Coordinator] Experiment {job.job_id} created")
    print(f"[Coordinator] Expression: {expression}")

    tasks = coordinator.create_tasks(job.job_id)
    assigned_tasks = coordinator.distribute_tasks(job.job_id)
    for task in assigned_tasks:
        print(
            f"[Coordinator] Task {task.task_id} -> Participant "
            f"{task.participant_id}: {task.expression}"
        )
        result = coordinator._participants[task.participant_id].execute_task(task)
        print(f"[Participant {result.participant_id}] Local result: {result.local_result}")
        coordinator.collect_result(result)

    final_result = coordinator.aggregate_results(job.job_id)
    print(f"[Coordinator] Global result: {final_result}")
    print(f"[Coordinator] Experiment {job.job_id} completed")
