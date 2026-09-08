from dataclasses import dataclass

from avatar_system.schemas.avatar import AvatarSpec


@dataclass
class SafetyResult:
    allowed: bool
    reasons: list[str]


class SafetyEngine:
    """
    Performs local safety checks on an AvatarSpec.

    This is intentionally deterministic and rule-based.
    """

    BLOCKED_TERMS = {
        "minor",
        "child",
        "children",
        "underage",
        "school child",
        "sexual",
        "explicit",
        "nude",
        "nudity",
    }

    def check(self, spec: AvatarSpec) -> SafetyResult:
        text = self._spec_to_text(spec).lower()

        violations = []

        for term in self.BLOCKED_TERMS:
            if term in text:
                violations.append(
                    f"Blocked term detected: '{term}'"
                )

        if violations:
            return SafetyResult(
                allowed=False,
                reasons=violations,
            )

        return SafetyResult(
            allowed=True,
            reasons=[],
        )

    @staticmethod
    def _spec_to_text(spec: AvatarSpec) -> str:
        return " ".join(
            [
                spec.age_band,
                spec.presentation,
                spec.skin_tone,
                spec.hair.style,
                spec.hair.color,
                spec.attire,
                spec.background,
                spec.pose,
                spec.geographic_context or "",
                " ".join(spec.reference_images),
            ]
        )