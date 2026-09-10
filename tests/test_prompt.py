from avatar_system.prompting.builder import PromptBuilder
from avatar_system.schemas.avatar import AvatarSpec


def test_prompt_contains_specification_attributes():
    spec = AvatarSpec(
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

    builder = PromptBuilder()

    prompt = builder.build(spec)

    assert "26-35" in prompt
    assert "professional" in prompt
    assert "short black hair" in prompt
    assert "formal business attire" in prompt


def test_negative_prompt_is_generated():
    spec = AvatarSpec(
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

    builder = PromptBuilder()

    negative_prompt = builder.build_negative_prompt(spec)

    assert "blurry" in negative_prompt
    assert "watermark" in negative_prompt
def test_prompt_includes_geographic_context():
    spec = AvatarSpec(
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
        geographic_context="South Asian",
    )

    builder = PromptBuilder()

    prompt = builder.build(spec)

    assert "South Asian" in prompt
def test_prompt_omits_missing_geographic_context():
    spec = AvatarSpec(
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
        geographic_context=None,
    )

    builder = PromptBuilder()

    prompt = builder.build(spec)

    assert "geographic context" not in prompt