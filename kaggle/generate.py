from pathlib import Path
import json

import torch
from diffusers import StableDiffusionXLPipeline


MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

INPUT_ROOT = Path("/kaggle/input")


def find_job_file():
    candidates = list(
        INPUT_ROOT.rglob("job.json")
    )

    if not candidates:
        raise FileNotFoundError(
            "No job.json found under /kaggle/input"
        )

    if len(candidates) > 1:
        raise RuntimeError(
            f"Multiple job.json files found: {candidates}"
        )

    return candidates[0]
OUTPUT_DIR = Path("/kaggle/working/avatar-output")

RESULT_FILE = OUTPUT_DIR / "result.json"


def load_job():
    job_file = find_job_file()

    print(f"Using job file: {job_file}")

    with open(job_file, "r", encoding="utf-8") as file:
        return json.load(file)

def load_pipeline():
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA GPU is required for image generation."
        )

    print("Loading SDXL...")

    pipeline = StableDiffusionXLPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True,
    )

    pipeline = pipeline.to("cuda")

    pipeline.enable_attention_slicing()

    print("SDXL loaded.")

    return pipeline


def generate_image(job):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    pipeline = load_pipeline()

    generation_spec = job["generation_spec"]
    prompt = job["prompt"]
    negative_prompt = job["negative_prompt"]

 

    seed = generation_spec.get("seed")

    if seed is None:
        seed = 42

    generator = torch.Generator(
        device="cuda"
    ).manual_seed(seed)
    print("=" * 60)
    print("PROMPT BEING SENT TO SDXL")
    print(prompt)
    print("=" * 60)
    print("NEGATIVE PROMPT")
    print(negative_prompt)
    print("=" * 60)
    print("GENERATION SETTINGS")
    print(f"width={generation_spec['width']}")
    print(f"height={generation_spec['height']}")
    print(f"steps={generation_spec['steps']}")
    print(f"guidance={generation_spec['guidance_scale']}")
    print(f"seed={seed}")
    print("=" * 60)

   

    result = pipeline(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=generation_spec["width"],
        height=generation_spec["height"],
        num_inference_steps=generation_spec["steps"],
        guidance_scale=generation_spec["guidance_scale"],
        num_images_per_prompt=1,
        generator=generator,
    )

    image_paths = []

    for index, image in enumerate(result.images):
        output_path = (
            OUTPUT_DIR
            / f'{job["job_id"]}_{index + 1}.png'
        )

        image.save(output_path)

        image_paths.append(str(output_path))

        print(f"Saved: {output_path}")

    return {
        "success": True,
        "job_id": job["job_id"],
        "model_name": MODEL_ID,
        "backend": "kaggle",
        "seed": seed,
        "output_paths": image_paths,
    }


def main():
    print("=" * 60)
    print("TRACK 02 AVATAR GENERATION WORKER")
    print("=" * 60)

    try:
        job = load_job()

        print(f"Job ID: {job['job_id']}")

        result = generate_image(job)

    except Exception as exc:
        result = {
            "success": False,
            "job_id": job.get("job_id")
            if "job" in locals()
            else None,
            "model_name": MODEL_ID,
            "backend": "kaggle",
            "error_message": str(exc),
        }

        print(
            f"Generation failed: {exc}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
        )

    print(f"Result written to: {RESULT_FILE}")

    if not result["success"]:
        raise RuntimeError(
            result["error_message"]
        )


if __name__ == "__main__":
    main()