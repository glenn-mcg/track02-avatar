from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from avatar_system.schemas.avatar import AvatarSpec
from avatar_system.schemas.generation import GenerationSpec


class JobStatus(str, Enum):
    CREATED = "created"
    PREPARED = "prepared"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATED = "validated"
    EVALUATED = "evaluated"


class JobBackend(str, Enum):
    LOCAL = "local"
    KAGGLE = "kaggle"


class GenerationJob(BaseModel):
    """
    A reproducible unit of avatar generation.
    """

    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(
        ...,
        min_length=1,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    status: JobStatus = JobStatus.CREATED

    avatar_spec: AvatarSpec

    generation_spec: GenerationSpec

    backend: JobBackend = JobBackend.LOCAL

    prompt: Optional[str] = None

    negative_prompt: Optional[str] = None

    output_path: Optional[str] = None

    error_message: Optional[str] = None