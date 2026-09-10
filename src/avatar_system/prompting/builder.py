from avatar_system.schemas.avatar import AvatarSpec


class PromptBuilder:
    """
    Converts a structured AvatarSpec into a deterministic
    image-generation prompt.
    """

    def build(self, spec: AvatarSpec) -> str:
        parts = [
            "A professional studio portrait of a fictional adult person,",
            f"age {spec.age_band},",
            "front-facing, natural expression,",
            f"{spec.hair.style} {spec.hair.color} hair,",
            f"{spec.attire},",
            "neutral professional background,",
            "realistic photography,",
            "soft studio lighting,",
            "high detail",
        ]

        if spec.geographic_context:
            parts.append(
                f"geographic context: {spec.geographic_context},"
            )

        return " ".join(parts)

    def build_negative_prompt(self, spec: AvatarSpec) -> str:
        return (
            "blurry, distorted face, deformed, extra fingers, "
            "extra limbs, low quality, duplicate person, "
            "text, watermark, logo"
        )