from pathlib import Path
import json
import time
from datetime import datetime, timezone

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

    width = generation_spec["width"]
    height = generation_spec["height"]
    steps = generation_spec["steps"]
    guidance_scale = generation_spec["guidance_scale"]

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
    print(f"width={width}")
    print(f"height={height}")
    print(f"steps={steps}")
    print(f"guidance={guidance_scale}")
    print(f"seed={seed}")
    print("=" * 60)

    # --------------------------------------------------
    # Benchmark / provenance information
    # --------------------------------------------------

    generation_started = datetime.now(
        timezone.utc
    )

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    # Synchronize so GPU timing is accurate
    torch.cuda.synchronize()

    inference_start = time.perf_counter()

    result = pipeline(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        num_images_per_prompt=1,
        generator=generator,
    )

    torch.cuda.synchronize()

    inference_seconds = (
        time.perf_counter()
        - inference_start
    )

    generation_completed = datetime.now(
        timezone.utc
    )

    # --------------------------------------------------
    # GPU information
    # --------------------------------------------------

    gpu_name = torch.cuda.get_device_name(0)

    gpu_memory_allocated = (
        torch.cuda.memory_allocated(0)
        / (1024 ** 2)
    )

    gpu_memory_peak = (
        torch.cuda.max_memory_allocated(0)
        / (1024 ** 2)
    )

    print("=" * 60)
    print("BENCHMARK INFORMATION")
    print("=" * 60)

    print(
        f"generation_started={generation_started.isoformat()}"
    )

    print(
        f"generation_completed={generation_completed.isoformat()}"
    )

    print(
        f"inference_seconds={inference_seconds:.3f}"
    )

    print(f"GPU name={gpu_name}")

    print(
        f"GPU memory allocated={gpu_memory_allocated:.2f} MB"
    )

    print(
        f"GPU memory peak={gpu_memory_peak:.2f} MB"
    )

    print(f"model={MODEL_ID}")
    print(f"seed={seed}")
    print(f"resolution={width}x{height}")
    print(f"steps={steps}")

    print("=" * 60)

    # --------------------------------------------------
    # Save generated images
    # --------------------------------------------------

    image_paths = []

    for index, image in enumerate(result.images):

        output_path = (
            OUTPUT_DIR
            / f'{job["job_id"]}_{index + 1}.png'
        )

        image.save(output_path)

        image_paths.append(str(output_path))

        print(f"Saved: {output_path}")

    # --------------------------------------------------
    # Return generation result + benchmark information
    # --------------------------------------------------

    return {
        "success": True,
        "job_id": job["job_id"],
        "model_name": MODEL_ID,
        "backend": "kaggle",
        "seed": seed,
        "output_paths": image_paths,

        "generation_started": (
            generation_started.isoformat()
        ),

        "generation_completed": (
            generation_completed.isoformat()
        ),

        "inference_seconds": round(
            inference_seconds,
            3,
        ),

        "gpu_name": gpu_name,

        "gpu_memory_allocated_mb": round(
            gpu_memory_allocated,
            2,
        ),

        "gpu_memory_peak_mb": round(
            gpu_memory_peak,
            2,
        ),

        "model_revision": MODEL_ID,

        "resolution": (
            f"{width}x{height}"
        ),

        "width": width,
        "height": height,

        "steps": steps,

        "guidance_scale": guidance_scale,
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