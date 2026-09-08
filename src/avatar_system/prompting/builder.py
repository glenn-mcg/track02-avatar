from avatar_system.schemas.avatar import AvatarSpec


class PromptBuilder:
    """
    Converts a structured AvatarSpec into a deterministic
    image-generation prompt.
    """

    def build(self, spec: AvatarSpec) -> str:
        parts = [
            "Professional adult avatar portrait.",
            f"Age range: {spec.age_band}.",
            f"Presentation: {spec.presentation}.",
            f"Skin tone: {spec.skin_tone}.",
            f"Hair: {spec.hair.style}, {spec.hair.color}.",
            f"Attire: {spec.attire}.",
            f"Background: {spec.background}.",
            f"Pose: {spec.pose}.",
        ]

        if spec.geographic_context:
            parts.append(
                f"Geographic context: {spec.geographic_context}."
            )

        parts.append(
            "High quality, natural appearance, "
            "realistic proportions, consistent facial structure."
        )

        return " ".join(parts)

    def build_negative_prompt(self, spec: AvatarSpec) -> str:
        return (
            "blurry, distorted, low quality, malformed anatomy, "
            "extra limbs, duplicate features, text, watermark"
        )