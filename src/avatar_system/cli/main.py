import json
from typing import Optional
import time
from pathlib import Path
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
def benchmark(
    job: Optional[str] = typer.Option(
        None,
        "--job",
        "-j",
        help="Generation job ID.",
    ),
):
    """
    Report benchmark and compute metrics for a completed generation job.
    """

    if job is None:
        typer.echo("ERROR: --job is required.")
        raise typer.Exit(code=1)

    output_directory = (
        Path("outputs")
        / job
        / "avatar-output"
    )

    result_file = output_directory / "result.json"

    if not result_file.exists():
        typer.echo(
            f"ERROR: Benchmark result not found: {result_file}"
        )
        typer.echo(
            "Run avatar generate --job <job_id> first."
        )
        raise typer.Exit(code=1)

    try:
        result = json.loads(
            result_file.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as exc:
        typer.echo(
            f"ERROR: Invalid result.json: {exc}"
        )
        raise typer.Exit(code=1)

    if not result.get("success"):
        typer.echo(
            "ERROR: Generation was not successful."
        )
        typer.echo(
            result.get(
                "error_message",
                "Unknown generation error.",
            )
        )
        raise typer.Exit(code=1)

    # --------------------------------------------------
    # Basic information
    # --------------------------------------------------

    job_id = result.get("job_id", job)

    model_name = result.get(
        "model_name",
        "unknown",
    )

    backend = result.get(
        "backend",
        "unknown",
    )

    seed = result.get("seed")

    resolution = result.get(
        "resolution",
        "unknown",
    )

    steps = result.get("steps")

    guidance_scale = result.get(
        "guidance_scale"
    )

    # --------------------------------------------------
    # Timing
    # --------------------------------------------------

    generation_started = result.get(
        "generation_started"
    )

    generation_completed = result.get(
        "generation_completed"
    )

    inference_seconds = result.get(
        "inference_seconds"
    )

    # --------------------------------------------------
    # Compute
    # --------------------------------------------------

    gpu_name = result.get(
        "gpu_name",
        "not recorded",
    )

    gpu_memory_allocated = result.get(
        "gpu_memory_allocated_mb"
    )

    gpu_memory_peak = result.get(
        "gpu_memory_peak_mb"
    )

    model_revision = result.get(
        "model_revision",
        model_name,
    )

    # --------------------------------------------------
    # Output
    # --------------------------------------------------

    output_paths = result.get(
        "output_paths",
        [],
    )

    image_count = len(output_paths)

    # --------------------------------------------------
    # Display
    # --------------------------------------------------

    typer.echo("")
    typer.echo("=" * 60)
    typer.echo("AVATAR GENERATION BENCHMARK")
    typer.echo("=" * 60)

    typer.echo("")
    typer.echo("JOB")
    typer.echo("-" * 60)
    typer.echo(f"Job ID: {job_id}")
    typer.echo(f"Backend: {backend}")
    typer.echo(f"Images: {image_count}")

    typer.echo("")
    typer.echo("MODEL")
    typer.echo("-" * 60)
    typer.echo(f"Model: {model_name}")
    typer.echo(f"Revision: {model_revision}")

    typer.echo("")
    typer.echo("GENERATION")
    typer.echo("-" * 60)
    typer.echo(f"Resolution: {resolution}")
    typer.echo(f"Steps: {steps}")
    typer.echo(f"Guidance scale: {guidance_scale}")
    typer.echo(f"Seed: {seed}")

    typer.echo("")
    typer.echo("TIMING")
    typer.echo("-" * 60)

    if generation_started:
        typer.echo(
            f"Generation started: {generation_started}"
        )

    if generation_completed:
        typer.echo(
            f"Generation completed: {generation_completed}"
        )

    if inference_seconds is not None:
        typer.echo(
            f"Inference time: "
            f"{inference_seconds:.3f} seconds"
        )

        if image_count > 0:
            typer.echo(
                f"Time per image: "
                f"{inference_seconds / image_count:.3f} seconds"
            )

    typer.echo("")
    typer.echo("COMPUTE")
    typer.echo("-" * 60)
    typer.echo(f"GPU: {gpu_name}")

    if gpu_memory_allocated is not None:
        typer.echo(
            f"GPU memory allocated: "
            f"{gpu_memory_allocated:.2f} MB"
        )
    else:
        typer.echo(
            "GPU memory allocated: not recorded"
        )

    if gpu_memory_peak is not None:
        typer.echo(
            f"GPU peak memory: "
            f"{gpu_memory_peak:.2f} MB"
        )
    else:
        typer.echo(
            "GPU peak memory: not recorded"
        )

    typer.echo("")
    typer.echo("OUTPUT")
    typer.echo("-" * 60)

    for output_path in output_paths:
        local_path = Path(output_path)

        # The Kaggle path is inside result.json,
        # so map it to our downloaded output directory.
        local_filename = local_path.name

        downloaded_path = (
            output_directory
            / local_filename
        )

        if downloaded_path.exists():
            file_size = downloaded_path.stat().st_size

            typer.echo(
                f"Image: {downloaded_path}"
            )

            typer.echo(
                f"File size: {file_size} bytes"
            )
        else:
            typer.echo(
                f"Image: {local_filename}"
            )
        # --------------------------------------------------
    # Save benchmark report
    # --------------------------------------------------

    benchmark_data = {
        "job_id": job_id,
        "backend": backend,
        "image_count": image_count,

        "model": model_name,
        "model_revision": model_revision,

        "resolution": resolution,
        "steps": steps,
        "guidance_scale": guidance_scale,
        "seed": seed,

        "generation_started": generation_started,
        "generation_completed": generation_completed,

        "inference_seconds": inference_seconds,
        "time_per_image_seconds": (
            inference_seconds / image_count
            if inference_seconds is not None and image_count > 0
            else None
        ),

        "gpu_name": gpu_name,
        "gpu_memory_allocated_mb": gpu_memory_allocated,
        "gpu_memory_peak_mb": gpu_memory_peak,

        "output_paths": output_paths,
    }

    benchmark_file = (
        Path("outputs")
        / job
        / "benchmark.json"
    )

    benchmark_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    benchmark_file.write_text(
        json.dumps(
            benchmark_data,
            indent=2,
        ),
        encoding="utf-8",
    )

    typer.echo("")
    typer.echo(
        f"Benchmark saved to: {benchmark_file}"
    )

    typer.echo("")
    typer.echo("=" * 60)
    typer.echo("BENCHMARK COMPLETE")
    typer.echo("=" * 60)

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