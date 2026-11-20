from flask import Flask, render_template, request

from src.coordinator.coordinator import Coordinator
from src.participant.participant_service import Participant


app = Flask(__name__)


def create_app() -> Flask:
    return app


@app.get("/")
def index():
    return render_template(
        "index.html",
        expression="(12 * 5) + (30 / 6) - (8 * 4) + (15 + 7)",
    )


@app.post("/run")
def run():
    expression = request.form.get("expression", "").strip()
    if not expression:
        return render_template(
            "index.html",
            expression=expression,
            error="Please enter an arithmetic expression.",
        )

    coordinator = Coordinator()
    coordinator.register_participant(Participant("A"))
    coordinator.register_participant(Participant("B"))
    timeline = [
        "Coordinator started",
        "Participant A registered",
        "Participant B registered",
    ]

    try:
        job = coordinator.start_training("JOB_001", expression)
        timeline.append("Experiment JOB_001 created")
        timeline.append(f"Expression received: {expression}")

        tasks = coordinator.create_tasks(job.job_id)
        timeline.append(f"{len(tasks)} training tasks created")

        assigned_tasks = coordinator.distribute_tasks(job.job_id)
        task_rows = []
        for task in assigned_tasks:
            participant = coordinator._participants[task.participant_id]
            timeline.append(
                f"Task {task.task_id} assigned to Participant {participant.participant_id}"
            )
            timeline.append(
                f"Participant {participant.participant_id} status changed to BUSY"
            )
            result = participant.execute_task(task)
            coordinator.collect_result(result)
            timeline.append(
                f"Participant {participant.participant_id} calculated "
                f"{task.expression} = {result.local_result}"
            )
            timeline.append(
                f"Participant {participant.participant_id} status changed to IDLE"
            )
            timeline.append(f"Coordinator collected result for {task.task_id}")
            task_rows.append(
                {
                    "task_id": task.task_id,
                    "participant_id": participant.participant_id,
                    "expression": task.expression,
                    "sign": task.sign,
                    "local_result": result.local_result,
                }
            )

        final_result = coordinator.aggregate_results(job.job_id)
        timeline.append("Coordinator aggregated all local results")
        timeline.append(f"Global result: {final_result}")
        timeline.append("Experiment JOB_001 completed")
        status = coordinator.get_training_status(job.job_id)

        return render_template(
            "index.html",
            expression=expression,
            timeline=timeline,
            task_rows=task_rows,
            status=status.status.value,
            final_result=final_result,
        )
    except Exception as exc:
        return render_template(
            "index.html",
            expression=expression,
            error=str(exc),
            timeline=timeline,
        )


if __name__ == "__main__":
    app.run(debug=True)
