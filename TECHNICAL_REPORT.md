# Technical Report
## Track 02 — Open-Source AI Human-Avatar Generation

## 1. Executive Summary

This project implements a modular open-source human-avatar generation system designed around a structured avatar specification rather than free-form user prompting.

The system accepts a validated JSON avatar specification containing age band, presentation, skin tone, hair, attire, background, pose, and optional geographic context/reference-image fields. A local CLI validates the specification, performs safety checks, generates a deterministic prompt, creates a reproducible generation job, routes image generation to the approved Kaggle free-compute execution path, downloads the generated assets, validates the returned output, evaluates basic image quality, records provenance/benchmark information, and stores the resulting manifest and artifacts.

The implementation deliberately separates local orchestration from accelerator-based model inference. This follows the assessment requirement that orchestration, safety, metadata, evaluation, and tests run locally on a non-GPU laptop while image-model inference may execute in a disclosed free accelerator notebook.

The current baseline uses Stable Diffusion XL (SDXL) through the Kaggle worker route. The project also keeps the generation backend behind an adapter interface so that another open model or conditioning approach can be evaluated without redesigning the CLI/job architecture.

## 2. Problem and Product Goal

The goal is to provide a reusable avatar-generation pipeline without relying on paid or proprietary commercial image-generation APIs.

The core data flow is:

```text
Avatar JSON
    ↓
Schema validation
    ↓
Safety check
    ↓
Prompt construction
    ↓
Generation job
    ↓
Kaggle dataset update
    ↓
Kaggle generation worker
    ↓
PNG output + result metadata
    ↓
Local output ingestion
    ↓
Validation
    ↓
Evaluation
    ↓
Benchmark + provenance manifest
```

The design treats appearance characteristics as neutral controllable attributes. Geographic context is optional and is not used as a substitute for nationality, ethnicity, or biometric identity.

## 3. Architecture

### 3.1 Main Components

```text
CLI
 │
 ├── prepare
 │     ├── AvatarSpec validation
 │     ├── safety checks
 │     ├── PromptBuilder
 │     └── JobManager
 │
 ├── generate
 │     └── GenerationOrchestrator
 │           └── GenerationAdapter
 │                 └── KaggleGenerator
 │                       ├── .kaggle_job/job.json
 │                       ├── Kaggle Dataset
 │                       ├── Kaggle Worker
 │                       └── downloaded outputs
 │
 ├── validate
 │     └── OutputValidator
 │
 ├── evaluate
 │     └── output-quality evaluation
 │
 └── benchmark
       └── timing / compute / generation metadata
```

### 3.2 Job-Based Design

Each generation is represented as a `GenerationJob`. The job contains:

- job ID
- creation timestamp
- avatar specification
- generation specification
- backend
- generated prompt
- negative prompt
- output/error information

Job IDs are automatically incremented by `JobManager`, preventing repeated manual IDs from overwriting earlier jobs.

A prepared job is stored locally under:

```text
jobs/<job_id>/job.json
```

This makes individual generations traceable and reproducible.

### 3.3 Generation Adapter

The generation layer uses an abstract `GenerationAdapter`.

This provides a stable interface:

```text
GenerationJob → GenerationResult
```

The current Kaggle implementation is one adapter. A local SDXL adapter is also present for environments with a compatible CUDA GPU, while the non-GPU laptop path reports that local SDXL inference is unavailable and directs generation through the permitted accelerator route.

This separation prevents Kaggle-specific execution details from leaking into the rest of the application.

### 3.4 Kaggle Execution Route

The local application:

1. Finds the prepared local `job.json`.
2. Copies it into `.kaggle_job/job.json`.
3. Versions the Kaggle dataset.
4. Pushes the Kaggle worker.
5. Waits for completion.
6. Downloads the worker output.
7. Reads `result.json`.
8. Locates the generated PNG.
9. Creates/saves the local provenance manifest.
10. Returns a project-level `GenerationResult`.

The important architectural distinction is that Kaggle is an execution environment, not the product architecture.

## 4. Data and Artifact Design

A successful generation produces an output bundle containing the generated image and metadata.

Representative structure:

```text
outputs/
└── job_007/
    ├── track-02-avatar-generation-worker.log
    └── avatar-output/
        ├── job_007_1.png
        ├── result.json
        └── avatar_manifest.json
```

The result metadata records the generation outcome, job ID, model, backend, seed, and output paths. The manifest extends this with project-level provenance and specification information.

The project also retains job specifications under `jobs/`, making it possible to trace a generated image back to the exact structured input.

## 5. Prompt Construction

Prompt generation is deterministic and based on the structured `AvatarSpec`.

The prompt builder includes attributes such as:

- age band
- presentation
- skin tone
- hair style
- hair colour
- attire
- background
- pose
- optional geographic context

The implementation avoids turning nationality into a visual stereotype. Geographic context is treated as an independent optional field.

Negative prompting is used to reduce common generation failures such as:

- malformed anatomy
- duplicate features
- extra limbs
- text/watermarks
- duplicate persons
- multiple faces

The project originally encountered a multi-person/multi-face generation failure. The generation prompt and negative controls were revised, and the resulting output was subsequently checked through the local validation/evaluation pipeline.

## 6. Reproducibility

Reproducibility is supported through:

- structured job specifications
- deterministic seeds
- recorded model name
- recorded generation parameters
- recorded resolution
- recorded inference steps
- recorded guidance scale
- recorded generation timestamps
- recorded GPU information where available
- recorded GPU memory measurements
- benchmark output
- retained Kaggle worker logs
- downloaded raw outputs
- provenance manifest

The project uses different deterministic seeds for the avatar test matrix rather than relying on a single seed for every test case.

For a fixed model revision, generation settings, prompt/specification, and seed, the intent is to make the run reproducible within the constraints of the execution environment.

## 7. Testing Strategy

The project includes automated tests covering the core engineering components.

The test suite covers areas including:

- schema validation
- job creation/loading
- automatic job ID generation
- prompt generation
- safety behaviour
- generation backend behaviour
- manifest creation
- output validation
- evaluation
- end-to-end orchestration behaviour

The test suite was brought to a passing baseline of 19 tests.

A local CPU-only environment is supported for the orchestration/test layer. The generation backend correctly reports the absence of a compatible local CUDA GPU instead of pretending that accelerator inference succeeded.

This distinction is important because the assessment explicitly separates local engineering execution from permitted free accelerator inference.

## 8. Evaluation and Benchmarking

The CLI provides:

```text
avatar validate --job <job_id>
avatar evaluate --job <job_id>
avatar benchmark --job <job_id>
```

Validation checks the generated artifacts and metadata.

Evaluation reports basic image-level properties such as:

- resolution
- file size
- brightness
- contrast
- quality score

Benchmarking records:

- generation start time
- generation completion time
- inference time
- time per image
- model
- model revision
- seed
- resolution
- steps
- guidance scale
- GPU name
- GPU memory allocated
- GPU peak memory

A representative benchmark run used a Tesla T4 and recorded approximately 35.2 seconds of inference for one 1024×1024 image with 30 inference steps.

Benchmark records are saved alongside the generated output metadata so the terminal display is not the only evidence.

## 9. Test Matrix

The project includes a balanced avatar matrix covering materially different appearance requirements while keeping geographic/cultural context separate from appearance attributes.

The matrix includes six primary avatar generations and four controlled single-attribute experiments.

The controlled experiments are intended to change one attribute while keeping the remaining specification stable. This provides a simple way to measure whether the prompt/specification change is reflected in the generated output.

The project records the corresponding specifications, jobs, generated images, validation results, evaluation results, and benchmark information.

## 10. Safety and Security

The system uses structured specifications and validation instead of allowing unrestricted prompt execution through the main workflow.

Safety controls include:

- schema validation
- explicit safety checks before job creation
- negative prompting
- avoidance of unsupported biometric claims
- fictional-avatar framing for the baseline
- no confidential/personal data in the accelerator workflow
- no consented-reference workflow unless appropriate consent and rights exist
- refusal/validation handling for unsafe requests
- explicit separation of appearance attributes from nationality labels

Reference images are represented as an optional field in the schema, leaving room for the exceptional consent-based workflow without making biometric identity claims part of the baseline system.

## 11. Privacy and Consent

The baseline generation workflow uses fictional avatars.

For any future individual-consistency/reference-image capability, explicit consent and rights to the reference images must be established before processing them.

The future implementation should additionally define:

- consent capture
- reference-image retention policy
- deletion workflow
- access controls
- synthetic-media labeling
- identity-consistency evaluation
- human review

These controls are intentionally treated as separate from the baseline fictional-avatar workflow.

## 12. Licensing and Open-Source Considerations

The project uses an openly available SDXL model through the disclosed free accelerator execution route.

Third-party software, model weights, and other sources are documented separately in `SOURCES.md`.

The project does not use a paid commercial generation API as its core generation mechanism.

The accelerator is treated as infrastructure for executing open-source/open-weight software rather than as the product itself.

## 13. Engineering Trade-offs

### Local CPU inference vs free accelerator

**Local CPU**

Advantages:
- fully local
- no external runtime dependency
- easier offline execution

Disadvantages:
- SDXL inference is impractical for the intended realistic generation workload
- high latency

**Kaggle free accelerator**

Advantages:
- practical SDXL inference
- suitable for the assessment's permitted free-compute route
- GPU memory is measurable
- worker execution can be logged and reproduced

Disadvantages:
- quota/availability limitations
- external execution dependency
- requires dataset/kernel synchronization

The chosen architecture keeps orchestration local while routing only model inference to the accelerator.

### One model vs model abstraction

Using one model keeps the baseline simpler and reduces integration risk. However, the adapter architecture makes a second open model or conditioning approach a natural extension for the Strong requirement.

### Prompt-based control vs reference conditioning

Prompt-based control is simple, inspectable, and suitable for fictional avatars.

Reference conditioning would provide stronger individual consistency, but introduces additional consent, privacy, identity-consistency, and evaluation requirements.

## 14. Failures and Debugging

Several practical failures were encountered during development.

### Multi-person output

An early generation produced multiple people/faces. The issue was investigated by tracing the actual prompt reaching the worker and checking the generated output rather than assuming that the local prompt builder was necessarily the prompt being executed.

The worker was instrumented to print the exact prompt, negative prompt, and generation settings before inference. This helped establish the actual generation input and separate stale-job/dataset issues from model behaviour.

### Stale Kaggle job input

A key integration issue was discovered when the local job changed but the Kaggle dataset still contained an older job file. The workflow was corrected so that the current local `job.json` is copied into `.kaggle_job` and the dataset is versioned before the worker runs.

### Local CUDA availability

The local generation backend correctly reports when no compatible CUDA GPU is available. This prevents a false-success path on the non-GPU laptop.

### Manifest serialization

A manifest-generation issue occurred when a Python `datetime` object was inserted directly into JSON serialization. The implementation was corrected so metadata is JSON serializable.

These failures are retained as useful engineering evidence rather than being hidden.

## 15. Alternatives Considered

### Django/API-first architecture

A Django API could expose job creation, status, artifact retrieval, and evaluation through HTTP endpoints.

For the assessment baseline, the local CLI was preferred because the mandatory interface is explicitly allowed to be a CLI and it reduces unnecessary web-service complexity.

The current modular architecture still allows a Django/REST layer to be added above the existing application services.

### Notebook-only implementation

A notebook-only system would be easier to demonstrate but would not meet the engineering expectations around local orchestration, CLI/API contracts, validation, testing, and maintainability.

The final architecture therefore uses the notebook only as the accelerator execution environment.

### Paid generation APIs

Commercial image APIs were not selected because the assessment explicitly prohibits paid/proprietary generation APIs for the core requirement.

## 16. Product Recommendation

The recommended baseline product architecture is:

```text
Structured Avatar Specification
          ↓
Local Validation + Safety
          ↓
Portable Generation Job
          ↓
Pluggable Generation Backend
          ↓
Generated Assets
          ↓
Validation + Evaluation
          ↓
Manifest + Benchmark + Evidence
```

This provides a clean foundation for reusable presenter identities and visual localisation while keeping the core system independent of commercial generation APIs.

The most valuable next product step is not a UI. It is improving measurable control and consistency.

## 17. Next Steps

### Strong-level improvements

1. Complete the balanced six-avatar matrix with documented coverage.
2. Complete at least four single-attribute controlled comparisons.
3. Quantify prompt/specification adherence using a repeatable scoring protocol.
4. Add a second open model or conditioning approach and compare results.
5. Improve the benchmark command to support repeated runs and aggregate statistics.
6. Add a documented human-review protocol.

### Exceptional-level improvements

1. Add a consented reference-image workflow.
2. Generate one individual consistently across at least five poses/backgrounds.
3. Generate two aspect ratios.
4. Use an independent embedding system for identity consistency.
5. Add human identity-consistency review.
6. Add synthetic-media labeling.
7. Add explicit privacy/deletion controls.
8. Demonstrate refusal when consent is absent.

## 18. Current Baseline Status

The current implementation has the major baseline engineering path operational:

- structured avatar specification
- validation
- safety checking
- deterministic job creation
- automatic job IDs
- prompt generation
- negative prompts
- local orchestration
- Kaggle dataset synchronization
- Kaggle worker execution
- generated PNG ingestion
- result metadata
- provenance manifest
- output validation
- evaluation
- benchmark reporting
- automated tests
- end-to-end test coverage
- reproducible seeds
- documented accelerator route

The remaining work should focus on strengthening evidence, documentation, controlled experiments, model comparison, and—if time permits—selected Strong/Exceptional capabilities rather than adding unnecessary product UI complexity.

## 19. Evidence and Submission Files

The submission should retain:

```text
README.md
SOURCES.md
AI_USE.md
TEST_PACK.md
TECHNICAL_REPORT.md
requirements/ or environment/lock file
tests/
examples/
jobs/
outputs/
kaggle/
.kaggle_job/
```

The repository should also include the exported Kaggle notebook/worker source and the exact reproduction instructions needed to execute the permitted accelerator path.

All material claims should be traceable to an artifact, test, benchmark record, log, or documented run.
