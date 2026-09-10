from avatar_system.generation.base import GenerationAdapter
from avatar_system.schemas.job import GenerationJob


class GenerationOrchestrator:
    """
    Executes a prepared generation job using a generation adapter.
    """

    def __init__(self, generator: GenerationAdapter):
        self.generator = generator

    def execute(self, job: GenerationJob):
        return self.generator.generate(job)