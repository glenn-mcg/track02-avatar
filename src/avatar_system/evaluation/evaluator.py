import json
from pathlib import Path

from PIL import Image, ImageStat


class AvatarEvaluator:
    """
    Performs basic objective evaluation of generated
    avatar images.
    """

    def evaluate(self, job_id: str) -> dict:

        output_directory = (
            Path("outputs")
            / job_id
            / "avatar-output"
        )

        result_file = output_directory / "result.json"

        if not result_file.exists():
            raise FileNotFoundError(
                f"Result file not found: {result_file}"
            )

        result_data = json.loads(
            result_file.read_text(
                encoding="utf-8"
            )
        )

        image_paths = sorted(
            output_directory.glob("*.png")
        )

        if not image_paths:
            raise FileNotFoundError(
                f"No PNG images found in "
                f"{output_directory}"
            )

        evaluations = []

        for image_path in image_paths:

            with Image.open(image_path) as image:

                width, height = image.size

                rgb_image = image.convert("RGB")

                statistics = ImageStat.Stat(
                    rgb_image
                )

                mean_brightness = (
                    sum(statistics.mean) / 3
                )

                extrema = rgb_image.getextrema()

                contrast = sum(
                    maximum - minimum
                    for minimum, maximum
                    in extrema
                ) / 3

                file_size = image_path.stat().st_size

                # ------------------------------------------
                # Simple quality indicators
                # ------------------------------------------

                resolution_score = (
                    1.0
                    if width >= 1024
                    and height >= 1024
                    else 0.7
                )

                brightness_score = (
                    1.0
                    if 35 <= mean_brightness <= 220
                    else 0.7
                )

                contrast_score = (
                    1.0
                    if contrast >= 30
                    else 0.7
                )

                file_score = (
                    1.0
                    if file_size >= 100_000
                    else 0.7
                )

                quality_score = (
                    resolution_score
                    + brightness_score
                    + contrast_score
                    + file_score
                ) / 4

                evaluations.append(
                    {
                        "file": str(image_path),
                        "width": width,
                        "height": height,
                        "file_size_bytes": file_size,
                        "mean_brightness": round(
                            mean_brightness,
                            2,
                        ),
                        "contrast": round(
                            contrast,
                            2,
                        ),
                        "quality_score": round(
                            quality_score * 100,
                            2,
                        ),
                    }
                )

        average_score = sum(
            item["quality_score"]
            for item in evaluations
        ) / len(evaluations)

        return {
            "job_id": job_id,
            "model_name": result_data.get(
                "model_name"
            ),
            "backend": result_data.get(
                "backend"
            ),
            "seed": result_data.get(
                "seed"
            ),
            "image_count": len(evaluations),
            "average_quality_score": round(
                average_score,
                2,
            ),
            "images": evaluations,
        }