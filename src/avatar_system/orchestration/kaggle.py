import json
import shutil
import subprocess
from pathlib import Path


class KaggleOrchestrator:
    """
    Handles submission of a generation job
    to a Kaggle GPU kernel and retrieves its output.
    """

    def __init__(
        self,
        kernel_directory: str = "kaggle",
        work_directory: str = ".kaggle_work",
        output_directory: str = "outputs",
    ):
        self.kernel_directory = Path(kernel_directory)

        self.work_directory = Path(
            work_directory
        )

        self.output_directory = Path(
            output_directory
        )

    def _run_command(self, command):
        print(
            "Running:",
            " ".join(command),
        )

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.stdout:
            print(result.stdout)

        if result.returncode != 0:
            if result.stderr:
                print(result.stderr)

            raise RuntimeError(
                "Kaggle command failed."
            )

        return result

    def prepare_job(self, job):
        job_directory = (
            self.work_directory
            / job.job_id
        )

        if job_directory.exists():
            shutil.rmtree(job_directory)

        job_directory.mkdir(
            parents=True
        )

        job_path = (
            job_directory
            / "job.json"
        )

        with open(
            job_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                job.model_dump(),
                file,
                indent=2,
            )

        return job_directory

    def submit(
        self,
        job,
    ):
        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        job_directory = self.prepare_job(
            job
        )

        print(
            f"Kaggle job prepared: {job.job_id}"
        )

        return job_directory