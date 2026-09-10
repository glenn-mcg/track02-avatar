from avatar_system.generation.local import LocalGenerator
from avatar_system.schemas.avatar import AvatarSpec
from avatar_system.schemas.generation import GenerationSpec
from avatar_system.schemas.job import GenerationJob


def test_local_generator():
    avatar_spec = AvatarSpec(
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

    generation_spec = GenerationSpec(
        seed=12345,
    )

    job = GenerationJob(
        job_id="test_job",
        avatar_spec=avatar_spec,
        generation_spec=generation_spec,
    )

    generator = LocalGenerator()

    result = generator.generate(job)

    assert result.success is True
    assert result.seed == 12345
    assert result.backend == "local"