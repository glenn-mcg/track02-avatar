import json
from typing import Optional
from avatar_system.jobs.manager import JobManager
from avatar_system.schemas.generation import GenerationSpec
from avatar_system.schemas.job import GenerationJob, JobBackend
from avatar_system.orchestration.orchestrator import Orchestrator

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

    job = GenerationJob(
        job_id="job_001",
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

    manager = JobManager()
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
        help="Generation job ID or job path.",
    ),
    backend: str = typer.Option(
        "local",
        "--backend",
        "-b",
        help="Generation backend.",
    ),
):
    """
    Generate an avatar from a prepared job.
    """
    print("WORKING: generate")


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