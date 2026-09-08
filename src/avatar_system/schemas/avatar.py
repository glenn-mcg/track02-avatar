from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HairSpec(BaseModel):
    """Hair-related attributes for an avatar."""

    model_config = ConfigDict(extra="forbid")

    style: str = Field(
        ...,
        min_length=1,
        description="Hair style."
    )

    color: str = Field(
        ...,
        min_length=1,
        description="Hair color."
    )


class AvatarSpec(BaseModel):
    """
    Complete specification describing the avatar to be generated.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(
        default="1.0",
        description="Version of the avatar specification schema."
    )

    age_band: str = Field(
        ...,
        min_length=1,
        description="Age band of the fictional adult avatar."
    )

    presentation: str = Field(
        ...,
        min_length=1,
        description="Overall presentation of the avatar."
    )

    skin_tone: str = Field(
        ...,
        min_length=1,
        description="Skin tone description."
    )

    hair: HairSpec

    attire: str = Field(
        ...,
        min_length=1,
        description="Clothing or attire description."
    )

    background: str = Field(
        ...,
        min_length=1,
        description="Background or environment."
    )

    pose: str = Field(
        ...,
        min_length=1,
        description="Pose description."
    )

    geographic_context: Optional[str] = Field(
        default=None,
        description="Optional geographic context."
    )

    reference_images: list[str] = Field(
        default_factory=list,
        description="Reference image paths or identifiers."
    )