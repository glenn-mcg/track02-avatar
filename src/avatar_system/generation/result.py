from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GenerationResult(BaseModel):
    """
    Result returned by a generation backend.
    """

    model_config = ConfigDict(extra="forbid")

    success: bool

    output_path: Optional[str] = None

    output_paths: list[str] = Field(
        default_factory=list
    )

    error_message: Optional[str] = None

    seed: Optional[int] = None

    model_name: Optional[str] = None

    backend: str