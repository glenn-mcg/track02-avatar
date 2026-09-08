from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict


class JobManifest(BaseModel):
    """
    Records provenance and execution information for a generation job.
    """

    model_config = ConfigDict(extra="forbid")

    job_id: str

    status: str

    model_name: str

    backend: str

    seed: Optional[int]

    prompt: Optional[str]

    negative_prompt: Optional[str]

    output_path: Optional[str]

    created_at: datetime

    completed_at: Optional[datetime] = None

    error_message: Optional[str] = None

    def mark_completed(self) -> None:
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)