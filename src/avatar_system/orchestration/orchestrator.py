from avatar_system.prompting.builder import PromptBuilder
from avatar_system.safety.engine import SafetyEngine
from avatar_system.schemas.job import GenerationJob


class Orchestrator:
    """
    Coordinates the preparation of a GenerationJob.
    """

    def __init__(
        self,
        safety_engine: SafetyEngine | None = None,
        prompt_builder: PromptBuilder | None = None,
    ):
        self.safety_engine = safety_engine or SafetyEngine()
        self.prompt_builder = prompt_builder or PromptBuilder()

    def prepare(self, job: GenerationJob) -> GenerationJob:
        # 1. Safety validation
        safety_result = self.safety_engine.check(
            job.avatar_spec
        )

        if not safety_result.allowed:
            reasons = "; ".join(safety_result.reasons)

            raise ValueError(
                f"Safety check failed: {reasons}"
            )

        # 2. Build prompt
        prompt = self.prompt_builder.build(
            job.avatar_spec
        )

        negative_prompt = (
            self.prompt_builder.build_negative_prompt(
                job.avatar_spec
            )
        )

        # 3. Attach generation information to job
        job.prompt = prompt
        job.negative_prompt = negative_prompt

        return job