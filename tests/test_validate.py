from pathlib import Path
import json


def test_valid_generated_output():
    """
    Verify that a successfully generated job contains
    the expected output artifacts and valid result metadata.
    """

    job_id = "job_004"

    job_file = Path("jobs") / job_id / "job.json"
    output_dir = Path("outputs") / job_id / "avatar-output"

    image_file = output_dir / f"{job_id}_1.png"
    result_file = output_dir / "result.json"

    assert job_file.exists(), "Job file is missing."
    assert image_file.exists(), "Generated image is missing."
    assert result_file.exists(), "result.json is missing."

    result = json.loads(
        result_file.read_text(encoding="utf-8")
    )

    assert result["success"] is True
    assert result["job_id"] == job_id
    assert result["backend"] == "kaggle"
    assert result["model_name"]
    assert result["seed"] is not None

    assert image_file.stat().st_size > 0


def test_result_file_is_valid_json():
    """
    result.json must always contain valid JSON.
    """

    result_file = (
        Path("outputs")
        / "job_004"
        / "avatar-output"
        / "result.json"
    )

    assert result_file.exists()

    data = json.loads(
        result_file.read_text(encoding="utf-8")
    )

    assert isinstance(data, dict)
    assert "success" in data
    assert "job_id" in data