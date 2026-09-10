from abc import ABC, abstractmethod

from avatar_system.schemas.job import GenerationJob
from avatar_system.generation.result import GenerationResult


class GenerationAdapter(ABC):
    """
    Common interface for all image-generation backends.
    """

    @abstractmethod
    def generate(self, job: GenerationJob) -> GenerationResult:
        """Generate an image for the supplied job."""
        raise NotImplementedError