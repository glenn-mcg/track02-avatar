import json
import shutil
import subprocess
import time
from pathlib import Path

from avatar_system.generation.base import GenerationAdapter
from avatar_system.generation.result import GenerationResult
from avatar_system.schemas.job import GenerationJob


class KaggleGenerator(GenerationAdapter):
    """
    Sends a generation job to Kaggle, waits for the
    worker to finish, and downloads the generated output.
    """

    KERNEL_ID = (
        "glennmcgrath/track-02-avatar-generation-worker"
    )

    DATASET_ID = (
        "glennmcgrath/avatar-generation-job"
    )

    DATASET_DIR = Path(".kaggle_job")

    KERNEL_DIR = Path("kaggle")

    OUTPUT_ROOT = Path("outputs")

    def generate(
        self,
        job: GenerationJob,
    ) -> GenerationResult:

        job_id = job.job_id

        print()
        print("=" * 60)
        print("KAGGLE GENERATION")
        print("=" * 60)

        print(f"Job ID: {job_id}")

        # --------------------------------------------------
        # 1. Find local job
        # --------------------------------------------------

        job_file = (
            Path("jobs")
            / job_id
            / "job.json"
        )

        if not job_file.exists():
            raise FileNotFoundError(
                f"Job file not found: {job_file}"
            )

        print(f"Local job: {job_file}")

        # --------------------------------------------------
        # 2. Copy job.json to Kaggle dataset directory
        # --------------------------------------------------

        self._prepare_dataset(job_file)

        # --------------------------------------------------
        # 3. Update Kaggle dataset
        # --------------------------------------------------

        self._push_dataset(job_id)

        # --------------------------------------------------
        # 4. Push Kaggle worker
        # --------------------------------------------------

        self._push_kernel()

        # --------------------------------------------------
        # 5. Wait for worker
        # --------------------------------------------------

        self._wait_for_kernel()

        # --------------------------------------------------
        # 6. Download output
        # --------------------------------------------------

        output_directory = (
            self.OUTPUT_ROOT / job_id
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._download_output(
            output_directory
        )

        # --------------------------------------------------
        # 7. Read result.json
        # --------------------------------------------------

        result_file = (
            output_directory
            / "avatar-output"
            / "result.json"
        )

        if not result_file.exists():
            raise RuntimeError(
                "Kaggle completed, but result.json "
                f"was not found at {result_file}"
            )

        result_data = json.loads(
            result_file.read_text(
                encoding="utf-8"
            )
        )

        # --------------------------------------------------
        # 8. Check generation result
        # --------------------------------------------------

        if not result_data.get("success"):
            raise RuntimeError(
                "Kaggle generation failed: "
                + str(
                    result_data.get(
                        "error_message",
                        "Unknown error",
                    )
                )
            )

        # --------------------------------------------------
        # 9. Find generated images
        # --------------------------------------------------

        avatar_output_directory = (
            output_directory
            / "avatar-output"
        )

        image_files = sorted(
            avatar_output_directory.glob("*.png")
        )

        if not image_files:
            raise RuntimeError(
                "Kaggle reported success, "
                "but no PNG image was downloaded."
            )

        image_paths = [
            str(path)
            for path in image_files
        ]

        print()
        print("=" * 60)
        print("KAGGLE GENERATION COMPLETE")
        print("=" * 60)

        for image_path in image_paths:
            print(f"Image: {image_path}")

        # --------------------------------------------------
        # 10. Return project's GenerationResult
        # --------------------------------------------------

        return GenerationResult(
            success=True,
            output_path=image_paths[0],
            output_paths=image_paths,
            seed=result_data.get("seed"),
            model_name=result_data.get(
                "model_name"
            ),
            backend="kaggle",
        )

    # ======================================================
    # DATASET
    # ======================================================

    def _prepare_dataset(
        self,
        job_file: Path,
    ):
        """
        Copy the current local job.json into
        the Kaggle dataset directory.
        """

        self.DATASET_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            self.DATASET_DIR / "job.json"
        )

        shutil.copy2(
            job_file,
            destination,
        )

        print()
        print(
            "Copied job to Kaggle dataset:"
        )
        print(destination)

    def _push_dataset(
        self,
        job_id: str,
    ):
        """
        Create a new version of the existing
        Kaggle dataset.
        """

        metadata_file = (
            self.DATASET_DIR
            / "dataset-metadata.json"
        )

        if not metadata_file.exists():
            raise FileNotFoundError(
                "Kaggle dataset metadata not found: "
                f"{metadata_file}"
            )

        command = [
            "kaggle",
            "datasets",
            "version",
            "-p",
            str(self.DATASET_DIR),
            "-m",
            f"Update generation job {job_id}",
        ]

        print()
        print(
            "Updating Kaggle dataset..."
        )

        self._run_command(command)

        print(
            "Kaggle dataset updated."
        )

    # ======================================================
    # KERNEL
    # ======================================================

    def _push_kernel(self):
        """
        Push the Kaggle generation worker.
        """

        command = [
            "kaggle",
            "kernels",
            "push",
            "-p",
            str(self.KERNEL_DIR),
        ]

        print()
        print(
            "Pushing Kaggle generation worker..."
        )

        self._run_command(command)

        print(
            "Kaggle worker pushed."
        )

    # ======================================================
    # WAIT
    # ======================================================

    def _wait_for_kernel(
        self,
        timeout_seconds: int = 1800,
        poll_seconds: int = 15,
    ):
        """
        Wait until the Kaggle worker completes.
        """

        print()
        print(
            "Waiting for Kaggle worker..."
        )

        start_time = time.time()

        while True:

            elapsed = (
                time.time() - start_time
            )

            if elapsed > timeout_seconds:
                raise TimeoutError(
                    "Kaggle generation timed out."
                )

            command = [
                "kaggle",
                "kernels",
                "status",
                self.KERNEL_ID,
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )

            output = (
                result.stdout
                + result.stderr
            ).strip()

            print(output)

            if "COMPLETE" in output:
                print(
                    "Kaggle worker completed."
                )
                return

            if "ERROR" in output:
                raise RuntimeError(
                    "Kaggle worker failed.\n"
                    + output
                )

            if "CANCEL" in output:
                raise RuntimeError(
                    "Kaggle worker was cancelled.\n"
                    + output
                )

            time.sleep(poll_seconds)

    # ======================================================
    # DOWNLOAD
    # ======================================================

    def _download_output(
        self,
        output_directory: Path,
    ):
        """
        Download the Kaggle worker output.
        """

        command = [
            "kaggle",
            "kernels",
            "output",
            self.KERNEL_ID,
            "-p",
            str(output_directory),
            "--force",
        ]

        print()
        print(
            "Downloading Kaggle output..."
        )

        self._run_command(command)

        print(
            f"Output downloaded to: "
            f"{output_directory}"
        )

    # ======================================================
    # COMMAND HELPER
    # ======================================================

    @staticmethod
    def _run_command(
        command: list[str],
    ):
        """
        Execute a Kaggle CLI command.
        """

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(result.stderr)

        if result.returncode != 0:
            raise RuntimeError(
                "Command failed:\n"
                + " ".join(command)
                + "\n\n"
                + result.stdout
                + "\n"
                + result.stderr
            )