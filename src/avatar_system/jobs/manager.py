import json
from pathlib import Path

from avatar_system.schemas.job import GenerationJob


class JobManager:
    """
    Creates, stores and loads generation jobs.
    """

    def __init__(self, jobs_directory: str = "jobs"):
        self.jobs_directory = Path(jobs_directory)
        self.jobs_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def next_job_id(self) -> str:
        """
        Return the next available sequential job ID.

        Example:
            job_001
            job_002
            job_003
        """

        existing_ids = []

        for path in self.jobs_directory.iterdir():
            if not path.is_dir():
                continue

            name = path.name

            if not name.startswith("job_"):
                continue

            number_part = name[4:]

            if number_part.isdigit():
                existing_ids.append(
                    int(number_part)
                )

        if not existing_ids:
            next_number = 1
        else:
            next_number = max(existing_ids) + 1

        return f"job_{next_number:03d}"

    def save(self, job: GenerationJob) -> Path:
        """
        Save a generation job to:

        jobs/<job_id>/job.json
        """

        job_directory = (
            self.jobs_directory / job.job_id
        )

        job_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        job_file = job_directory / "job.json"

        job_file.write_text(
            job.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return job_file

    def load(self, job_id: str) -> GenerationJob:
        """
        Load an existing generation job.
        """

        job_file = (
            self.jobs_directory
            / job_id
            / "job.json"
        )

        if not job_file.exists():
            raise FileNotFoundError(
                f"Job not found: {job_id}"
            )

        data = json.loads(
            job_file.read_text(
                encoding="utf-8"
            )
        )

        return GenerationJob.model_validate(data)