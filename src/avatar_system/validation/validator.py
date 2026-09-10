import json
from pathlib import Path

from PIL import Image

from avatar_system.schemas.job import GenerationJob


class OutputValidator:
    """
    Validates generated avatar output and its provenance.
    """

    def validate(self, job: GenerationJob) -> dict:
        job_id = job.job_id

        output_directory = (
            Path("outputs")
            / job_id
            / "avatar-output"
        )

        result_file = output_directory / "result.json"

        errors = []
        warnings = []

        # --------------------------------------------------
        # 1. Check result.json
        # --------------------------------------------------

        if not result_file.exists():
            errors.append(
                f"Result file not found: {result_file}"
            )

            return self._result(
                job_id=job_id,
                valid=False,
                errors=errors,
                warnings=warnings,
            )

        try:
            result_data = json.loads(
                result_file.read_text(
                    encoding="utf-8"
                )
            )
        except json.JSONDecodeError as exc:
            errors.append(
                f"Invalid result.json: {exc}"
            )

            return self._result(
                job_id=job_id,
                valid=False,
                errors=errors,
                warnings=warnings,
            )

        # --------------------------------------------------
        # 2. Check generation success
        # --------------------------------------------------

        if not result_data.get("success"):
            errors.append(
                "Generation result reports failure."
            )

        # --------------------------------------------------
        # 3. Check job ID provenance
        # --------------------------------------------------

        result_job_id = result_data.get("job_id")

        if result_job_id != job_id:
            errors.append(
                "Job ID mismatch: "
                f"expected {job_id}, "
                f"got {result_job_id}"
            )

        # --------------------------------------------------
        # 4. Check backend
        # --------------------------------------------------

        backend = result_data.get("backend")

        if backend != "kaggle":
            warnings.append(
                f"Output backend is '{backend}', "
                "expected 'kaggle'."
            )

        # --------------------------------------------------
        # 5. Check model
        # --------------------------------------------------

        model_name = result_data.get(
            "model_name"
        )

        if not model_name:
            warnings.append(
                "Model name is missing from provenance."
            )

        # --------------------------------------------------
        # 6. Find output images
        # --------------------------------------------------

        image_paths = sorted(
            output_directory.glob("*.png")
        )

        if not image_paths:
            errors.append(
                "No generated PNG image found."
            )

        # --------------------------------------------------
        # 7. Validate images
        # --------------------------------------------------

        for image_path in image_paths:
            try:
                with Image.open(image_path) as image:

                    image.verify()

                with Image.open(image_path) as image:

                    width, height = image.size

                    if width <= 0 or height <= 0:
                        errors.append(
                            f"Invalid image dimensions: "
                            f"{image_path}"
                        )

                    if width < 512 or height < 512:
                        warnings.append(
                            f"Low resolution image: "
                            f"{image_path} "
                            f"({width}x{height})"
                        )

            except Exception as exc:
                errors.append(
                    f"Invalid image {image_path}: {exc}"
                )

        # --------------------------------------------------
        # 8. Validate against GenerationSpec
        # --------------------------------------------------

        expected_width = job.generation_spec.width
        expected_height = job.generation_spec.height

        for image_path in image_paths:
            try:
                with Image.open(image_path) as image:
                    width, height = image.size

                    if (
                        width != expected_width
                        or height != expected_height
                    ):
                        warnings.append(
                            f"{image_path.name}: "
                            f"expected "
                            f"{expected_width}x{expected_height}, "
                            f"got {width}x{height}"
                        )

            except Exception:
                pass

        valid = len(errors) == 0

        return self._result(
            job_id=job_id,
            valid=valid,
            errors=errors,
            warnings=warnings,
            image_count=len(image_paths),
            model_name=model_name,
            backend=backend,
        )

    @staticmethod
    def _result(
        job_id: str,
        valid: bool,
        errors: list[str],
        warnings: list[str],
        image_count: int = 0,
        model_name: str | None = None,
        backend: str | None = None,
    ) -> dict:

        return {
            "valid": valid,
            "job_id": job_id,
            "image_count": image_count,
            "model_name": model_name,
            "backend": backend,
            "errors": errors,
            "warnings": warnings,
        }