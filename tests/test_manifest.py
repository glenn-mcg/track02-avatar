import json
from pathlib import Path

from avatar_system.generation.manifest import ManifestBuilder
from avatar_system.generation.result import GenerationResult
from avatar_system.schemas.job import GenerationJob


def test_manifest_contains_required_sections():
    """
    Verify that the provenance manifest contains
    all required assessment information.
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

    result = GenerationResult(
        success=True,
        output_path=(
            "outputs/job_004/avatar-output/job_004_1.png"
        ),
        output_paths=[
            "outputs/job_004/avatar-output/job_004_1.png"
        ],
        error_message=None,
        seed=42,
        model_name=(
            "stabilityai/stable-diffusion-xl-base-1.0"
        ),
        backend="kaggle",
    )

    builder = ManifestBuilder()

    manifest = builder.build(
        job=job,
        result=result,
    )

    assert "avatar_spec" in manifest
    assert "generation_spec" in manifest
    assert "prompt" in manifest
    assert "negative_prompt" in manifest
    assert "model" in manifest
    assert "generation" in manifest
    assert "provenance" in manifest
    assert "safety" in manifest
    assert "compute_route" in manifest
    assert "output" in manifest


def test_manifest_is_json_serializable():
    """
    Regression test for the datetime serialization bug.
    """

    job_file = (
        Path("jobs")
        / "job_004"
        / "job.json"
    )

    job_data = json.loads(
        job_file.read_text(encoding="utf-8")
    )

    job = GenerationJob.model_validate(job_data)

    result = GenerationResult(
        success=True,
        output_paths=[
            "job_004_1.png"
        ],
        seed=42,
        model_name=(
            "stabilityai/stable-diffusion-xl-base-1.0"
        ),
        backend="kaggle",
    )

    builder = ManifestBuilder()

    manifest = builder.build(
        job,
        result,
    )

    # This would previously fail with:
    # Object of type datetime is not JSON serializable
    serialized = json.dumps(manifest)

    assert serialized