from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GenerationSpec(BaseModel):
    """
    Configuration controlling one image-generation request.
    """

    model_config = ConfigDict(extra="forbid")

    model_name: str = Field(
        default="default",
        min_length=1,
        description="Model used for image generation.",
    )

    width: int = Field(
        default=1024,
        ge=256,
        le=2048,
    )

    height: int = Field(
        default=1024,
        ge=256,
        le=2048,
    )

    steps: int = Field(
        default=30,
        ge=1,
        le=100,
    )

    guidance_scale: float = Field(
        default=7.0,
        ge=0.0,
        le=30.0,
    )

    seed: Optional[int] = Field(
        default=None,
        ge=0,
    )

    num_images: int = Field(
        default=1,
        ge=1,
        le=4,
    )

    negative_prompt: str = ""

    backend: str = Field(
        default="local",
        min_length=1,
    )