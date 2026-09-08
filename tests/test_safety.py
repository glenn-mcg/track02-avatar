from avatar_system.safety.engine import SafetyEngine
from avatar_system.schemas.avatar import AvatarSpec


def create_spec(**overrides):
    data = {
        "age_band": "26-35",
        "presentation": "professional",
        "skin_tone": "medium",
        "hair": {
            "style": "short",
            "color": "black",
        },
        "attire": "formal business attire",
        "background": "professional office",
        "pose": "front facing portrait",
    }

    data.update(overrides)

    return AvatarSpec(**data)


def test_safe_spec_is_allowed():
    engine = SafetyEngine()

    spec = create_spec()

    result = engine.check(spec)

    assert result.allowed is True
    assert result.reasons == []


def test_unsafe_spec_is_blocked():
    engine = SafetyEngine()

    spec = create_spec(
        age_band="child"
    )

    result = engine.check(spec)

    assert result.allowed is False
    assert len(result.reasons) > 0