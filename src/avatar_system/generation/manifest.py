import json
from datetime import datetime, timezone
from pathlib import Path

from avatar_system.schemas.job import GenerationJob
from avatar_system.generation.result import GenerationResult


class ManifestBuilder:
    """
    Builds the final provenance manifest for a generated avatar.
    """

    def build(
        self,
        job: GenerationJob,
        result: GenerationResult,
    ) -> dict:
        """
        Create a complete avatar generation manifest.
        """

        output_paths = result.output_paths.copy()

        if not output_paths and result.output_path:
            output_paths = [result.output_path]

        manifest = {
            "manifest_version": "1.0",

            # --------------------------------------------------
            # Job identity
            # --------------------------------------------------

            "job": {
                "job_id": job.job_id,
                "created_at": job.created_at.isoformat(),
                "status": "completed",
            },

            # --------------------------------------------------
            # Avatar specification
            # --------------------------------------------------

            "avatar_spec": job.avatar_spec.model_dump(
                mode="json"
            ),

            # --------------------------------------------------
            # Generation specification
            # --------------------------------------------------

            "generation_spec": (
                job.generation_spec.model_dump(
                    mode="json"
                )
            ),

            # --------------------------------------------------
            # Exact prompts used
            # --------------------------------------------------

            "prompt": job.prompt,

            "negative_prompt": job.negative_prompt,

            # --------------------------------------------------
            # Model / checkpoint
            # --------------------------------------------------

            "model": {
                "model_name": result.model_name,
                "checkpoint": result.model_name,
            },

            # --------------------------------------------------
            # Reproducibility
            # --------------------------------------------------

            "generation": {
                "seed": result.seed,
                "width": job.generation_spec.width,
                "height": job.generation_spec.height,
                "steps": job.generation_spec.steps,
                "guidance_scale": (
                    job.generation_spec.guidance_scale
                ),
                "num_images": (
                    job.generation_spec.num_images
                ),
            },

            # --------------------------------------------------
            # Provenance
            # --------------------------------------------------

            "provenance": {
                "job_id": job.job_id,
                "backend": result.backend,
                "generated_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "orchestrator": "Track 02 Avatar Generation System",
            },

            # --------------------------------------------------
            # Safety
            # --------------------------------------------------

            "safety": {
                "status": "passed",
                "source": "avatar specification validation",
            },

            # --------------------------------------------------
            # Compute route
            # --------------------------------------------------

            "compute_route": {
                "backend": result.backend,
                "route": (
                    "Kaggle GPU worker"
                    if result.backend == "kaggle"
                    else result.backend
                ),
            },

            # --------------------------------------------------
            # Output
            # --------------------------------------------------

            "output": {
                "success": result.success,
                "image_count": len(output_paths),
                "images": output_paths,
                "result_file": "result.json",
            },
        }

        return manifest

    def save(
        self,
        manifest: dict,
        output_directory: Path,
    ) -> Path:
        """
        Save avatar_manifest.json beside the generated image.
        """

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        manifest_file = (
            output_directory
            / "avatar_manifest.json"
        )

        manifest_file.write_text(
            json.dumps(
                manifest,
                indent=2,
            ),
            encoding="utf-8",
        )

        return manifest_file