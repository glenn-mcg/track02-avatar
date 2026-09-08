import json
from pathlib import Path

from avatar_system.schemas.job import GenerationJob


class JobManager:
    """
    Creates, stores and loads generation jobs.
    """

    def __init__(self, jobs_directory: str = "jobs"):
        self.jobs_directory = Path(jobs_directory)
        self.jobs_directory.mkdir(parents=True, exist_ok=True)

    def save(self, job: GenerationJob) -> Path:
        job_directory = self.jobs_directory / job.job_id
        job_directory.mkdir(parents=True, exist_ok=True)

        job_file = job_directory / "job.json"

        job_file.write_text(
            job.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return job_file

    def load(self, job_id: str) -> GenerationJob:
        job_file = self.jobs_directory / job_id / "job.json"

        if not job_file.exists():
            raise FileNotFoundError(
                f"Job not found: {job_id}"
            )

        data = json.loads(
            job_file.read_text(encoding="utf-8")
        )

        return GenerationJob.model_validate(data)