from src.computation.expression_engine import ExpressionEngine
from src.models.training_job import TrainingJob, TrainingJobStatus
from src.models.training_result import TrainingResult
from src.models.training_task import TrainingTask
from src.participant.participant_service import Participant


class Coordinator:
    def __init__(self, engine: ExpressionEngine | None = None):
        self._engine = engine or ExpressionEngine()
        self._participants: dict[str, Participant] = {}
        self._jobs: dict[str, TrainingJob] = {}

    def register_participant(self, participant: Participant) -> None:
        if participant.participant_id in self._participants:
            raise ValueError(f"Participant {participant.participant_id} is already registered")
        self._participants[participant.participant_id] = participant

    def start_training(self, job_id: str, expression: str) -> TrainingJob:
        if not self._participants:
            raise ValueError("At least one participant is required")
        if job_id in self._jobs:
            raise ValueError(f"Job {job_id} already exists")
        self._engine.parse(expression)
        job = TrainingJob(job_id=job_id, expression=expression)
        self._jobs[job_id] = job
        return job

    def create_tasks(self, job_id: str) -> list[TrainingTask]:
        job = self._get_job(job_id)
        if job.tasks:
            raise ValueError(f"Tasks have already been created for job {job_id}")
        task_specs = self._engine.decompose(job.expression)
        job.tasks = [
            TrainingTask(
                task_id=f"{job_id}_TASK_{spec.position}",
                job_id=job_id,
                expression=spec.expression,
                position=spec.position,
                sign=spec.sign,
            )
            for spec in task_specs
        ]
        return job.tasks

    def distribute_tasks(self, job_id: str) -> list[TrainingTask]:
        job = self._get_job(job_id)
        if not job.tasks:
            raise ValueError("Create tasks before distributing them")
        participant_ids = list(self._participants)
        assigned = [
            TrainingTask(
                task_id=task.task_id,
                job_id=task.job_id,
                expression=task.expression,
                position=task.position,
                sign=task.sign,
                participant_id=participant_ids[index % len(participant_ids)],
            )
            for index, task in enumerate(job.tasks)
        ]
        job.tasks = assigned
        job.status = TrainingJobStatus.RUNNING
        return assigned

    def collect_result(self, result: TrainingResult) -> None:
        job, task = self._find_task(result.task_id)
        if result.participant_id not in self._participants:
            raise ValueError(f"Unknown participant {result.participant_id}")
        if task.participant_id != result.participant_id:
            raise ValueError(f"Task {task.task_id} is assigned to another participant")
        if result.task_id in job.results:
            raise ValueError(f"Result for task {result.task_id} has already been submitted")
        job.results[result.task_id] = result

    def aggregate_results(self, job_id: str) -> int | float:
        job = self._get_job(job_id)
        if not job.tasks:
            raise ValueError("No tasks exist for this job")
        if len(job.results) != len(job.tasks):
            raise ValueError("Cannot aggregate until all task results are collected")
        job.final_result = sum(
            task.sign * job.results[task.task_id].local_result
            for task in sorted(job.tasks, key=lambda item: item.position)
        )
        job.status = TrainingJobStatus.COMPLETED
        return job.final_result

    def get_training_status(self, job_id: str) -> TrainingJob:
        return self._get_job(job_id)

    def _get_job(self, job_id: str) -> TrainingJob:
        if job_id not in self._jobs:
            raise ValueError(f"Unknown job {job_id}")
        return self._jobs[job_id]

    def _find_task(self, task_id: str) -> tuple[TrainingJob, TrainingTask]:
        for job in self._jobs.values():
            for task in job.tasks:
                if task.task_id == task_id:
                    return job, task
        raise ValueError(f"Unknown task {task_id}")
