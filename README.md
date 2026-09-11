# Track 02 — Open-Source AI Human-Avatar Generation

An open-source AI human-avatar generation system developed for the **IncuBrix Track 02 Candidate Project Assessment**.

The system accepts a structured avatar specification, validates and safety-checks the request, creates a reproducible generation job, executes image generation using an openly available model on an approved free GPU execution route, downloads and validates the generated output, evaluates the image, records provenance and benchmark information, and produces reproducible output artifacts.

---

## 1. Project Overview

The system is designed around a **local orchestration architecture**.

The local machine is responsible for:

- Avatar specification validation
- Safety checks
- Prompt construction
- Job creation and management
- Job ID generation
- Generation orchestration
- Kaggle execution control
- Output download
- Output validation
- Avatar evaluation
- Manifest/provenance generation
- Benchmark reporting
- Automated tests

Image-model inference is executed through a disclosed Kaggle GPU notebook because SDXL inference is impractical on a typical CPU-only laptop.

The generation model used is:

```
stabilityai/stable-diffusion-xl-base-1.0
```

---

## 2. Repository

GitHub repository:

[https://github.com/glenn-mcg/track02-avatar](https://github.com/glenn-mcg/track02-avatar)

---

## 3. System Architecture

```text
Avatar Specification JSON
          |
          v
   avatar prepare
          |
          v
 Specification Validation
          |
          v
      Safety Check
          |
          v
    Prompt Builder
          |
          v
   Generation Job
   jobs/job_xxx/
          |
          v
   Kaggle Generator
          |
          +----------------------+
          |                      |
          v                      v
 Copy job.json              Kaggle Worker
 to .kaggle_job/                  |
          |                       v
          |                SDXL Image Generation
          |                       |
          |                       v
          |                 result.json
          |                 generated PNG
          |                       |
          +----------<------------+
                    |
                    v
             Local Outputs
          outputs/job_xxx/
                    |
          +---------+---------+
          |         |         |
          v         v         v
       Validate  Evaluate  Benchmark
                    |
                    v
          avatar_manifest.json
```

---

## 4. Technology Stack

- Python 3.13.7
- Pydantic
- Typer
- Pytest
- PyTorch
- Hugging Face Diffusers
- Stable Diffusion XL
- Kaggle Notebooks
- Kaggle CLI
- Pillow
- JSON-based job specifications

Local orchestration runs on a non-GPU laptop.

**Tested local hardware:**

| Component | Spec |
|---|---|
| CPU | Intel Core i3, 4 cores |
| RAM | 8 GB |
| Python | 3.13.7 |

GPU inference was executed using a Kaggle Tesla T4 environment.

---

## 5. Project Structure

```text
track02-avatar/
│
├── examples/
│   ├── avatar_001.json
│   ├── avatar_002.json
│   ├── ...
│   └── avatar_020.json
│
├── jobs/
│   ├── job_001/
│   │   └── job.json
│   ├── job_002/
│   │   └── job.json
│   └── ...
│
├── outputs/
│   ├── job_xxx/
│   │   ├── avatar-output/
│   │   │   ├── job_xxx_1.png
│   │   │   ├── result.json
│   │   │   └── avatar_manifest.json
│   │   └── ...
│
├── src/
│   └── avatar_system/
│       ├── cli/
│       ├── generation/
│       ├── schemas/
│       ├── safety/
│       └── ...
│
├── tests/
│   ├── test_schema.py
│   ├── test_prompt.py
│   ├── test_safety.py
│   ├── test_job.py
│   ├── test_generation.py
│   ├── test_generation_backend.py
│   ├── test_manifest.py
│   ├── test_validate.py
│   ├── test_evalaution.py
│   └── test_end_to_end.py
│
├── kaggle/
│   ├── kernel-metadata.json
│   └── generate.py
│
├── .kaggle_job/
│   ├── dataset-metadata.json
│   └── job.json
│
├── SOURCES.md
├── AI_USE.md
├── TEST_PACK.md
├── TECHNICAL_REPORT.md
├── requirements.txt
└── README.md
```

---

## 6. Installation

Clone the repository:

```bash
git clone https://github.com/glenn-mcg/track02-avatar.git
cd track02-avatar
```

Create a virtual environment:

**Windows**

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Verify the CLI:

```bash
avatar --help
```

---

## 7. Configuration

The project uses configuration rather than requiring hardcoded local output paths.

The Kaggle integration requires the Kaggle CLI to be installed and authenticated according to Kaggle's official instructions.

The project does **not** require:

- A paid generation API
- A commercial image-generation API
- A payment card
- Pay-as-you-go compute

The image-generation workload is executed through the disclosed free Kaggle GPU route.

---

## 8. Prepare a Job

Avatar specifications are represented as JSON.

**Example:**

```json
{
  "schema_version": "1.0",
  "age_band": "26-35",
  "presentation": "professional",
  "skin_tone": "medium",
  "hair": {
    "style": "short",
    "color": "black"
  },
  "attire": "formal business attire",
  "background": "professional office",
  "pose": "front facing portrait",
  "geographic_context": null,
  "reference_images": []
}
```

Prepare the specification:

```bash
avatar prepare --spec examples/avatar_001.json
```

The CLI:

1. Loads the specification.
2. Validates the schema.
3. Performs the safety check.
4. Builds the generation prompt.
5. Creates the next available job ID.
6. Saves the generation job.

**Example output:**

```text
Specification is valid.
Safety check passed.
Prompt generated.
Job created: job_001
Job file: jobs\job_001\job.json
```

---

## 9. Reproducible Seeds

Generation jobs contain a generation seed.

For reproducible benchmark experiments, a deterministic seed should be explicitly assigned to each test job.

**Example:**

```json
"generation_spec": {
  "model_name": "default",
  "width": 1024,
  "height": 1024,
  "steps": 30,
  "guidance_scale": 7.0,
  "seed": 42,
  "num_images": 1,
  "negative_prompt": "",
  "backend": "local"
}
```

Different experimental avatars can use different seeds.

The seed is preserved in:

- `job.json`
- `result.json`
- `avatar_manifest.json`
- benchmark output

---

## 10. Generate an Avatar

After preparing a job:

```bash
avatar generate --job job_001
```

The generation pipeline:

1. Loads the local job.
2. Copies `job.json` into `.kaggle_job`.
3. Updates the Kaggle input dataset.
4. Pushes the Kaggle worker.
5. Waits for the worker to complete.
6. Downloads the generated output.
7. Reads `result.json`.
8. Locates the generated image.
9. Creates the local generation result.
10. Creates the avatar provenance manifest.

The generated files are stored under:

```
outputs/job_001/avatar-output/
```

---

## 11. Kaggle Generation Worker

The Kaggle worker executes:

```
stabilityai/stable-diffusion-xl-base-1.0
```

The worker:

- Loads the job from the Kaggle input dataset.
- Reads the exact prompt from `job.json`.
- Reads the negative prompt.
- Uses the configured resolution.
- Uses the configured inference steps.
- Uses the configured guidance scale.
- Uses the configured seed.
- Generates the image.
- Records generation metadata.
- Writes the generated PNG.
- Writes `result.json`.

The Kaggle dataset is updated before each generation so that the worker receives the current job rather than an older job specification.

---

## 12. Validate Generated Output

Run:

```bash
avatar validate --job job_001
```

Validation checks the returned generation output and provenance.

**Example:**

```text
============================================================
OUTPUT VALIDATION
============================================================
Job ID: job_001
Images: 1
Backend: kaggle
Model: stabilityai/stable-diffusion-xl-base-1.0

VALIDATION PASSED.
```

The validator checks that the expected output artifacts and generation metadata are present and valid.

---

## 13. Evaluate Generated Output

Run:

```bash
avatar evaluate --job job_001
```

**Example:**

```text
============================================================
AVATAR EVALUATION
============================================================
Job ID: job_001
Backend: kaggle
Model: stabilityai/stable-diffusion-xl-base-1.0
Images evaluated: 1
Average quality score: 100.0/100
```

The evaluation records image-level measurements including:

- Resolution
- File size
- Brightness
- Contrast
- Quality score

---

## 14. Benchmark

Run:

```bash
avatar benchmark --job job_001
```

The benchmark records:

- Job ID
- Backend
- Number of images
- Model
- Model revision
- Resolution
- Steps
- Guidance scale
- Seed
- Generation start time
- Generation completion time
- Inference time
- Time per image
- GPU name
- GPU memory allocated
- GPU peak memory
- Output image
- Output file size

**Example:**

```text
============================================================
AVATAR GENERATION BENCHMARK
============================================================

JOB
------------------------------------------------------------
Job ID: job_007
Backend: kaggle
Images: 1

MODEL
------------------------------------------------------------
Model: stabilityai/stable-diffusion-xl-base-1.0
Revision: stabilityai/stable-diffusion-xl-base-1.0

GENERATION
------------------------------------------------------------
Resolution: 1024x1024
Steps: 30
Guidance scale: 7.0
Seed: 42

TIMING
------------------------------------------------------------
Generation started: ...
Generation completed: ...
Inference time: ...
Time per image: ...

COMPUTE
------------------------------------------------------------
GPU: Tesla T4
GPU memory allocated: ...
GPU peak memory: ...

OUTPUT
------------------------------------------------------------
Image: ...
File size: ...

============================================================
BENCHMARK COMPLETE
============================================================
```

Benchmark information is also persisted so that the results are not dependent only on terminal output.

---

## 15. Manifest

Each successful generation produces:

```
avatar_manifest.json
```

The manifest records generation provenance including:

- Job information
- Avatar specification
- Prompt
- Negative prompt
- Seed
- Model
- Model revision
- Backend
- Compute route
- Generation metadata
- Output information
- Safety/provenance information

The manifest is stored with the generated output:

```text
outputs/
└── job_xxx/
    └── avatar-output/
        ├── job_xxx_1.png
        ├── result.json
        └── avatar_manifest.json
```

This allows an output image to be traced back to the exact job specification and generation configuration.

---

## 16. Test Suite

Run all automated tests with:

```bash
pytest -q
```

The test suite covers:

- Schema validation
- Prompt construction
- Safety checks
- Job creation and loading
- Generation backend behaviour
- Manifest generation
- Output validation
- Evaluation
- End-to-end workflow

The project includes unit, integration and end-to-end tests.

Generation tests avoid requiring a local GPU where appropriate and verify the expected failure behaviour when SDXL cannot run locally.

---

## 17. Test Matrix

The assessment test matrix includes fictional avatars with materially different appearance requirements.

The experiments vary attributes such as:

- Skin tone
- Hair style
- Hair colour
- Attire
- Background
- Age band
- Geographic context

Geographic context is treated as a contextual attribute rather than a claim about biological or national identity.

The test matrix also includes controlled single-attribute changes where the remaining specification is held constant.

The purpose is to measure whether the generation system follows the requested specification without using nationality as a stereotype.

---

## 18. Safety

The system is designed to reject or prevent unsafe/disallowed generation requests during job preparation.

Safety checks occur before generation.

The system also avoids representing generated fictional avatars as verified real people or as biometric truths.

Reference images are optional in the schema and are intended only for appropriately consented use.

---

## 19. Privacy and Reference Images

Reference-image functionality is designed around consent.

The current baseline workflow uses fictional avatar specifications without requiring personal reference images.

Reference images should only be used where the required consent and rights are available.

Personal or confidential data should not be uploaded to the hosted compute environment.

---

## 20. Open-Source Model

The generation model used by the worker is:

```
stabilityai/stable-diffusion-xl-base-1.0
```

Model licensing and attribution information is documented separately in `SOURCES.md`.

The project does not use a paid proprietary image-generation API as its core generation mechanism.

---

## 21. Reproduction Workflow

A clean reproduction follows this sequence:

```bash
git clone https://github.com/glenn-mcg/track02-avatar.git
cd track02-avatar

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

avatar prepare --spec examples/avatar_001.json

avatar generate --job job_001

avatar validate --job job_001

avatar evaluate --job job_001

avatar benchmark --job job_001

pytest -q
```

The exact generated job ID should be taken from the `avatar prepare` output.

---

## 22. Evidence

The repository contains the major evidence required for assessment:

- `README.md`
- `SOURCES.md`
- `AI_USE.md`
- `TEST_PACK.md`
- `TECHNICAL_REPORT.md`
- `requirements.txt`
- `tests/`
- `examples/`
- `jobs/`
- `outputs/`
- `kaggle/`

Generated outputs contain the generated images and associated metadata.

The Kaggle worker source and notebook/kernel configuration are included so that the hosted execution route can be inspected and reproduced.

---

## 23. Known Limitations

- SDXL inference is not practical on the tested 8 GB CPU-only laptop.
- GPU execution therefore uses an approved free accelerator route.
- Free accelerator availability and quota are external constraints.
- Generation quality can vary depending on model sampling and prompt interpretation.
- Geographic context is treated as an appearance/localisation attribute and is not intended to infer nationality or ethnicity.
- The baseline system does not claim biometric identity verification.
- Reference-image identity consistency is outside the baseline fictional-avatar workflow.

---

## 24. Future Extensions

Possible future extensions include:

- Additional open model comparison
- More systematic prompt/spec adherence scoring
- Independent identity embedding evaluation
- Human review scoring
- Five-pose identity consistency experiments
- Multiple aspect-ratio experiments
- More detailed compute benchmarking
- Improved caching and resume support
- Expanded API interface
- Optional UI
- Stronger privacy/deletion controls for consented reference-image workflows

---

## 25. Assessment Date

Submission preparation date:

**11 September 2026**

---

## 26. Ownership and Disclosure

AI coding tools were used during development as disclosed in `AI_USE.md`.

The candidate remains responsible for understanding, testing and modifying the submitted implementation.

Third-party models, libraries and resources are documented in `SOURCES.md`.

---

## 27. Final Run

The recommended demonstration path is:

```bash
avatar prepare --spec examples/avatar_001.json
avatar generate --job <generated_job_id>
avatar validate --job <generated_job_id>
avatar evaluate --job <generated_job_id>
avatar benchmark --job <generated_job_id>
pytest -q
```
