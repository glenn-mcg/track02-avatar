import json
from typing import Optional
from avatar_system.jobs.manager import JobManager
from avatar_system.schemas.generation import GenerationSpec
from avatar_system.schemas.job import GenerationJob, JobBackend
from avatar_system.orchestration.orchestrator import Orchestrator
from avatar_system.generation.local import LocalGenerator
from avatar_system.jobs.manager import JobManager
from avatar_system.orchestration.generation import GenerationOrchestrator

import typer
from pydantic import ValidationError

from avatar_system.schemas.avatar import AvatarSpec

app = typer.Typer(
    name="avatar",
    help="IncuBrix Track 02 Avatar Generation System.",
    no_args_is_help=True,
)

@app.command()
def prepare(
    spec: Optional[str] = typer.Option(
        None,
        "--spec",
        "-s",
        help="Path to the avatar specification JSON file.",
    ),
):
    """
    Validate an avatar specification and create a generation job.
    """

    if spec is None:
        typer.echo("ERROR: --spec is required.")
        raise typer.Exit(code=1)

    try:
        with open(spec, "r", encoding="utf-8") as file:
            data = json.load(file)

        avatar_spec = AvatarSpec.model_validate(data)

    except FileNotFoundError:
        typer.echo(f"ERROR: Specification file not found: {spec}")
        raise typer.Exit(code=1)

    except json.JSONDecodeError as exc:
        typer.echo(f"ERROR: Invalid JSON: {exc}")
        raise typer.Exit(code=1)

    except ValidationError as exc:
        typer.echo("ERROR: Invalid avatar specification.")
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    generation_spec = GenerationSpec()

    generation_spec = GenerationSpec()

    manager = JobManager()

    job_id = manager.next_job_id()

    job = GenerationJob(
        job_id=job_id,
        avatar_spec=avatar_spec,
        generation_spec=generation_spec,
        backend=JobBackend.LOCAL,
    )
    orchestrator = Orchestrator()

    try:
        job = orchestrator.prepare(job)
    except ValueError as exc:
        typer.echo(f"ERROR: {exc}")
        raise typer.Exit(code=1)
    job_file = manager.save(job)

    typer.echo("Specification is valid.")
    typer.echo("Safety check passed.")
    typer.echo("Prompt generated.")
    typer.echo(f"Job created: {job.job_id}")
    typer.echo(f"Job file: {job_file}")


    

@app.command()
def generate(
    job: Optional[str] = typer.Option(
        None,
        "--job",
        "-j",
        help="Generation job ID.",
    ),
):
    """
    Generate an avatar from a prepared job.
    """

    if job is None:
        typer.echo("ERROR: --job is required.")
        raise typer.Exit(code=1)

    manager = JobManager()

    try:
        generation_job = manager.load(job)
    except FileNotFoundError as exc:
        typer.echo(f"ERROR: {exc}")
        raise typer.Exit(code=1)

    generator = LocalGenerator()

    orchestrator = GenerationOrchestrator(
        generator=generator
    )

    try:
        result = orchestrator.execute(
            generation_job
        )
    except Exception as exc:
        typer.echo(
            f"ERROR: Generation failed: {exc}"
        )
        raise typer.Exit(code=1)

    if not result.success:
        typer.echo(
            f"ERROR: Generation failed: "
            f"{result.error_message}"
        )
        raise typer.Exit(code=1)

    typer.echo("Generation completed.")
    typer.echo(f"Backend: {result.backend}")
    typer.echo(f"Model: {result.model_name}")
    typer.echo(f"Seed: {result.seed}")
    typer.echo(f"Output: {result.output_path}")

@app.command()
def validate(
    job: Optional[str] = typer.Option(
        None,
        "--job",
        "-j",
        help="Generation job ID or job path.",
    ),
):
    """
    Validate the generated output and provenance.
    """
    print("WORKING: validate")


@app.command()
def evaluate(
    job: Optional[str] = typer.Option(
        None,
        "--job",
        "-j",
        help="Generation job ID or job path.",
    ),
):
    """
    Evaluate generated avatar outputs.
    """
    print("WORKING: evaluate")


@app.command()
def status(
    job: Optional[str] = typer.Option(
        None,
        "--job",
        "-j",
        help="Generation job ID or job path.",
    ),
):
    """
    Show the status of a generation job.
    """
    print("WORKING: status")


@app.command()
def version():
    """
    Show the application version.
    """
    print("track02-avatar 0.1.0")


if __name__ == "__main__":
    app()