from avatar_system.schemas.generation import GenerationSpec


def test_generation_spec_defaults():
    spec = GenerationSpec()

    assert spec.width == 1024
    assert spec.height == 1024
    assert spec.steps == 30
    assert spec.backend == "kaggle"


def test_generation_spec_custom_values():
    spec = GenerationSpec(
        model_name="test-model",
        width=768,
        height=768,
        steps=40,
        guidance_scale=8.0,
        seed=12345,
        backend="kaggle",
    )

    assert spec.model_name == "test-model"
    assert spec.width == 768
    assert spec.seed == 12345
    assert spec.backend == "kaggle"