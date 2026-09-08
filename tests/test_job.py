from avatar_system.schemas.avatar import AvatarSpec
from avatar_system.schemas.generation import GenerationSpec
from avatar_system.schemas.job import (
    GenerationJob,
    JobBackend,
    JobStatus,
)


def create_avatar_spec():
    return AvatarSpec(
        age_band="26-35",
        presentation="professional",
        skin_tone="medium",
        hair={
            "style": "short",
            "color": "black",
        },
        attire="formal business attire",
        background="professional office",
        pose="front facing portrait",
    )


def test_generation_job_creation():
    avatar_spec = create_avatar_spec()

    generation_spec = GenerationSpec(
        seed=12345,
        backend="local",
    )

    job = GenerationJob(
        job_id="job_001",
        avatar_spec=avatar_spec,
        generation_spec=generation_spec,
        backend=JobBackend.LOCAL,
    )

    assert job.job_id == "job_001"
    assert job.status == JobStatus.CREATED
    assert job.generation_spec.seed == 12345