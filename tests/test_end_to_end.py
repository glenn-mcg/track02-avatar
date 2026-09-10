import json
from pathlib import Path

from PIL import Image

from avatar_system.generation.manifest import ManifestBuilder
from avatar_system.generation.result import GenerationResult
from avatar_system.schemas.job import GenerationJob


def test_end_to_end_job_to_manifest(tmp_path):
    """
    End-to-end local test:

    prepared job
        -> fake generation
        -> image output
        -> result metadata
        -> provenance manifest
    """

    job_file = (
        Path("jobs")
        / "job_004"
        / "job.json"
    )

    assert job_file.exists()

    job_data = json.loads(
        job_file.read_text(encoding="utf-8")
    )

    job = GenerationJob.model_validate(job_data)

    output_directory = (
        tmp_path
        / job.job_id
        / "avatar-output"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Fake local generation
    # ---------------------------------------------------------

    image_path = (
        output_directory
        / f"{job.job_id}_1.png"
    )

    image = Image.new(
        "RGB",
        (
            job.generation_spec.width,
            job.generation_spec.height,
        ),
    )

    image.save(image_path)

    # ---------------------------------------------------------
    # Generation result
    # ---------------------------------------------------------

    result = GenerationResult(
        success=True,
        output_path=str(image_path),
        output_paths=[str(image_path)],
        seed=42,
        model_name=(
            "stabilityai/stable-diffusion-xl-base-1.0"
        ),
        backend="local-test",
    )

    # ---------------------------------------------------------
    # Build manifest
    # ---------------------------------------------------------

    builder = ManifestBuilder()

    manifest = builder.build(
        job=job,
        result=result,
    )

    manifest_path = builder.save(
        manifest=manifest,
        output_directory=output_directory,
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert image_path.exists()
    assert image_path.stat().st_size > 0

    assert manifest_path.exists()

    saved_manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        saved_manifest["job"]["job_id"]
        == job.job_id
    )

    assert (
        saved_manifest["generation"]["seed"]
        == 42
    )

    assert (
        saved_manifest["model"]["model_name"]
        == "stabilityai/stable-diffusion-xl-base-1.0"
    )

    assert (
        saved_manifest["compute_route"]["backend"]
        == "local-test"
    )

    assert (
        saved_manifest["safety"]["status"]
        == "passed"
    )

    assert (
        saved_manifest["output"]["success"]
        is True
    )