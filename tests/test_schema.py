import pytest
from pydantic import ValidationError

from avatar_system.schemas.avatar import AvatarSpec


def test_valid_avatar_spec():
    spec = AvatarSpec(
        schema_version="1.0",
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

    assert spec.age_band == "26-35"
    assert spec.hair.style == "short"
    assert spec.hair.color == "black"


def test_reference_images_default_to_empty_list():
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

    assert spec.reference_images == []


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        AvatarSpec(
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
            unknown_field="not_allowed",
        )


def test_empty_hair_style_is_rejected():
    with pytest.raises(ValidationError):
        AvatarSpec(
            age_band="26-35",
            presentation="professional",
            skin_tone="medium",
            hair={
                "style": "",
                "color": "black",
            },
            attire="formal business attire",
            background="professional office",
            pose="front facing portrait",
        )