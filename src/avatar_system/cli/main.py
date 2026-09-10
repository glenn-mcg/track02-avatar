import json
from typing import Optional
from avatar_system.jobs.manager import JobManager
from avatar_system.schemas.generation import GenerationSpec
from avatar_system.schemas.job import GenerationJob, JobBackend
from avatar_system.orchestration.orchestrator import Orchestrator
from avatar_system.generation.local import LocalGenerator
from avatar_system.jobs.manager import JobManager
from avatar_system.orchestration.generation import GenerationOrchestrator
from avatar_system.generation.kaggle import KaggleGenerator
from avatar_system.validation.validator import OutputValidator
from avatar_system.evaluation.evaluator import AvatarEvaluator

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

    generator = KaggleGenerator()

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
def validate(
    job: Optional[str] = typer.Option(
        None,
        "--job",
        "-j",
        help="Generation job ID.",
    ),
):
    """
    Validate the generated output and provenance.
    """

    if job is None:
        typer.echo(
            "ERROR: --job is required."
        )
        raise typer.Exit(code=1)

    manager = JobManager()

    try:
        generation_job = manager.load(job)

    except FileNotFoundError as exc:
        typer.echo(f"ERROR: {exc}")
        raise typer.Exit(code=1)

    validator = OutputValidator()

    try:
        result = validator.validate(
            generation_job
        )

    except Exception as exc:
        typer.echo(
            f"ERROR: Validation failed: {exc}"
        )
        raise typer.Exit(code=1)

    typer.echo("")
    typer.echo("=" * 60)
    typer.echo("OUTPUT VALIDATION")
    typer.echo("=" * 60)

    typer.echo(
        f"Job ID: {result['job_id']}"
    )

    typer.echo(
        f"Images: {result['image_count']}"
    )

    typer.echo(
        f"Backend: {result['backend']}"
    )

    typer.echo(
        f"Model: {result['model_name']}"
    )

    if result["valid"]:
        typer.echo("")
        typer.echo("VALIDATION PASSED.")
    else:
        typer.echo("")
        typer.echo("VALIDATION FAILED.")

    if result["warnings"]:
        typer.echo("")
        typer.echo("Warnings:")

        for warning in result["warnings"]:
            typer.echo(f"  - {warning}")

    if result["errors"]:
        typer.echo("")
        typer.echo("Errors:")

        for error in result["errors"]:
            typer.echo(f"  - {error}")

    if not result["valid"]:
        raise typer.Exit(code=1)
@app.command()
def evaluate(
    job: Optional[str] = typer.Option(
        None,
        "--job",
        "-j",
        help="Generation job ID.",
    ),
):
    """
    Evaluate generated avatar outputs.
    """

    if job is None:
        typer.echo(
            "ERROR: --job is required."
        )
        raise typer.Exit(code=1)

    manager = JobManager()

    try:
        manager.load(job)

    except FileNotFoundError as exc:
        typer.echo(f"ERROR: {exc}")
        raise typer.Exit(code=1)

    evaluator = AvatarEvaluator()

    try:
        result = evaluator.evaluate(job)

    except Exception as exc:
        typer.echo(
            f"ERROR: Evaluation failed: {exc}"
        )
        raise typer.Exit(code=1)

    typer.echo("")
    typer.echo("=" * 60)
    typer.echo("AVATAR EVALUATION")
    typer.echo("=" * 60)

    typer.echo(
        f"Job ID: {result['job_id']}"
    )

    typer.echo(
        f"Backend: {result['backend']}"
    )

    typer.echo(
        f"Model: {result['model_name']}"
    )

    typer.echo(
        f"Images evaluated: "
        f"{result['image_count']}"
    )

    typer.echo(
        f"Average quality score: "
        f"{result['average_quality_score']}/100"
    )

    typer.echo("")

    for image in result["images"]:

        typer.echo(
            f"Image: {image['file']}"
        )

        typer.echo(
            f"  Resolution: "
            f"{image['width']}x{image['height']}"
        )

        typer.echo(
            f"  File size: "
            f"{image['file_size_bytes']} bytes"
        )

        typer.echo(
            f"  Brightness: "
            f"{image['mean_brightness']}"
        )

        typer.echo(
            f"  Contrast: "
            f"{image['contrast']}"
        )

        typer.echo(
            f"  Quality score: "
            f"{image['quality_score']}/100"
        )

        typer.echo("")


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