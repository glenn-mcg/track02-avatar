from pathlib import Path

import torch
from diffusers import StableDiffusionXLPipeline

from avatar_system.generation.base import GenerationAdapter
from avatar_system.generation.result import GenerationResult
from avatar_system.schemas.job import GenerationJob


class LocalGenerator(GenerationAdapter):
    """
    SDXL image-generation backend.

    The same backend can run on a CUDA GPU locally
    or inside a GPU-enabled environment such as Kaggle.
    """

    def __init__(
        self,
        model_id: str = "stabilityai/stable-diffusion-xl-base-1.0",
        output_directory: str = "outputs",
    ):
        self.model_id = model_id
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.pipeline = None

    def _check_device(self) -> str:
        if torch.cuda.is_available():
            return "cuda"

        raise RuntimeError(
            "No CUDA GPU detected. "
            "SDXL local inference requires a GPU for this project. "
            "Run the generation backend in the permitted Kaggle GPU environment."
        )

    def _load_pipeline(self):
        if self.pipeline is not None:
            return

        device = self._check_device()

        print(f"Loading model: {self.model_id}")
        print(f"Using device: {device}")

        self.pipeline = StableDiffusionXLPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True,
        )

        self.pipeline = self.pipeline.to(device)

        self.pipeline.enable_attention_slicing()

    def generate(
        self,
        job: GenerationJob,
    ) -> GenerationResult:

        try:
            self._load_pipeline()

            generation_spec = job.generation_spec

            seed = generation_spec.seed

            if seed is None:
                seed = torch.seed()

            generator = torch.Generator(
                device="cuda"
            ).manual_seed(seed)

            output = self.pipeline(
                prompt=job.prompt,
                negative_prompt=job.negative_prompt,
                width=generation_spec.width,
                height=generation_spec.height,
                num_inference_steps=generation_spec.steps,
                guidance_scale=generation_spec.guidance_scale,
                num_images_per_prompt=generation_spec.num_images,
                generator=generator,
            )

            image_paths = []

            for index, image in enumerate(output.images):
                filename = (
                    f"{job.job_id}_{index + 1}.png"
                )

                output_path = (
                    self.output_directory / filename
                )

                image.save(output_path)

                image_paths.append(str(output_path))

            first_output = (
                image_paths[0]
                if image_paths
                else None
            )

            return GenerationResult(
        success=True,
        output_path=first_output,
        output_paths=image_paths,
        seed=seed,
        model_name=self.model_id,
        backend="local",
    )

        except Exception as exc:
            return GenerationResult(
                success=False,
                output_path=None,
                seed=job.generation_spec.seed,
                model_name=self.model_id,
                backend="local",
                error_message=str(exc),
            )