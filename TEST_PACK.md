# Track 02 — Test Pack

## Purpose

This test pack documents verification evidence for the Open-Source AI
Human-Avatar Generation system.

It covers specification validation, job creation, prompt generation,
safety checks, generation routing, output validation, evaluation,
provenance/manifest handling, end-to-end testing, benchmarking, the
six-avatar test matrix, controlled attribute tests, and negative cases.

## Standard Run Path

``` text
Avatar specification JSON
        |
        v
avatar prepare --spec <spec.json>
        |
        v
Generation job
        |
        v
avatar generate --job <job_id>
        |
        +--> local orchestration
        +--> copy job.json to .kaggle_job/
        +--> update Kaggle dataset
        +--> push Kaggle worker
        +--> run open-weight SDXL
        +--> download output
        |
        v
avatar validate --job <job_id>
        |
        v
avatar evaluate --job <job_id>
        |
        v
avatar benchmark --job <job_id>
```

## Six-Avatar Test Matrix

| Test | Input                      | Job       | Purpose            | Result    |
|------|----------------------------|-----------|--------------------|-----------|
| A01  | `examples/avatar_011.json` | `job_009` | Fictional avatar 1 | Generated |
| A02  | `examples/avatar_012.json` | `job_010` | Fictional avatar 2 | Generated |
| A03  | `examples/avatar_013.json` | `job_011` | Fictional avatar 3 | Generated |
| A04  | `examples/avatar_014.json` | `job_012` | Fictional avatar 4 | Generated |
| A05  | `examples/avatar_015.json` | `job_013` | Fictional avatar 5 | Generated |
| A06  | `examples/avatar_016.json` | `job_014` | Fictional avatar 6 | Generated |

Generated assets are retained under:

``` text
outputs/job_009/
outputs/job_010/
outputs/job_011/
outputs/job_012/
outputs/job_013/
outputs/job_014/
```

The specifications use neutral appearance attributes rather than
treating nationality as a visual stereotype.

## Four Controlled Attribute Tests

| Test | Input                      | Controlled attribute | Purpose                              |
|------|----------------------------|----------------------|--------------------------------------|
| C01  | `examples/avatar_017.json` | Skin tone            | Verify controlled appearance change  |
| C02  | `examples/avatar_018.json` | Hair                 | Verify controlled hair change        |
| C03  | `examples/avatar_019.json` | Attire               | Verify controlled clothing change    |
| C04  | `examples/avatar_020.json` | Background           | Verify controlled environment change |

Expected behaviour: the requested attribute changes while the remaining
specification is kept stable as far as practical, and the generated
prompt/output records the requested specification.

## Automated Tests

Tests are located in:

``` text
tests/
```

Current modules include:

``` text
tests/test_schema.py
tests/test_job.py
tests/test_generation.py
tests/test_generation_backend.py
tests/test_prompt.py
tests/test_safety.py
tests/test_validate.py
tests/test_evalaution.py
tests/test_manifest.py
tests/test_end_to_end.py
```

The complete local suite reached:

``` text
19 passed
```

## Validation Evidence

Command:

``` powershell
avatar validate --job <job_id>
```

Recorded successful example:

``` text
============================================================
OUTPUT VALIDATION
============================================================
Job ID: job_004
Images: 1
Backend: kaggle
Model: stabilityai/stable-diffusion-xl-base-1.0

VALIDATION PASSED.
```

Validation checks the expected generated artifacts and metadata.

## Evaluation Evidence

Command:

``` powershell
avatar evaluate --job <job_id>
```

Recorded example:

``` text
============================================================
AVATAR EVALUATION
============================================================
Job ID: job_004
Backend: kaggle
Model: stabilityai/stable-diffusion-xl-base-1.0
Images evaluated: 1
Average quality score: 100.0/100

Image: outputs\job_004vatar-output\job_004_1.png
Resolution: 1024x1024
File size: 1626147 bytes
Brightness: 122.87
Contrast: 242.0
Quality score: 100.0/100
```

The automated score is an engineering output-quality check, not a claim
of human-perception ground truth.

## Benchmark Evidence

Command:

``` powershell
avatar benchmark --job <job_id>
```

Recorded example:

``` text
Job ID: job_007
Backend: kaggle
Images: 1
Model: stabilityai/stable-diffusion-xl-base-1.0
Revision: stabilityai/stable-diffusion-xl-base-1.0
Resolution: 1024x1024
Steps: 30
Guidance scale: 7.0
Seed: 42
Inference time: 35.197 seconds
Time per image: 35.197 seconds
GPU: Tesla T4
GPU memory allocated: 6734.25 MB
GPU peak memory: 9967.01 MB
Image: outputs\job_007vatar-output\job_007_1.png
File size: 1373895 bytes
```

Benchmark output is saved in the job output area as well as printed to
the terminal.

## Provenance / Manifest Evidence

A successful generation retains:

``` text
outputs/<job_id>/avatar-output/
```

with the generated PNG and generation metadata.

Example generation result:

``` json
{
  "success": true,
  "job_id": "job_004",
  "model_name": "stabilityai/stable-diffusion-xl-base-1.0",
  "backend": "kaggle",
  "seed": 42,
  "output_paths": [
    "/kaggle/working/avatar-output/job_004_1.png"
  ]
}
```

The project also generates `avatar_manifest.json` through:

``` text
src/avatar_system/generation/manifest.py
tests/test_manifest.py
```

## Negative / Failure Cases

### Invalid or Ambiguous Specification

Command:

``` powershell
avatar prepare --spec <invalid-or-ambiguous-spec.json>
```

Expected behaviour:

``` text
ERROR: Invalid avatar specification.
```

The invalid specification must not create a generation job.

Evidence:

``` text
tests/test_schema.py
tests/test_job.py
```

### Unsafe Request

Command:

``` powershell
avatar prepare --spec <unsafe-spec.json>
```

Expected behaviour: the request is rejected by the safety checks before
generation.

Evidence:

``` text
tests/test_safety.py
```

### Corrupted Output

The validator is designed to reject missing or invalid generated
artifacts.

Command:

``` powershell
avatar validate --job <job_id>
```

Expected behaviour:

``` text
VALIDATION FAILED.
```

This case is retained as validator capability; a corrupted production
artifact is not required to be kept in the final generated-output set.

## Evidence Index

| Claim                                         | Evidence                                                                                   |
|-----------------------------------------------|--------------------------------------------------------------------------------------------|
| Structured avatar specification               | `src/avatar_system/schemas/avatar.py`                                                      |
| Generation job schema                         | `src/avatar_system/schemas/job.py`                                                         |
| Generation configuration                      | `src/avatar_system/schemas/generation.py`                                                  |
| Automatic job IDs                             | `src/avatar_system/job/manager.py`                                                         |
| Prompt construction                           | `src/avatar_system/prompt/builder.py`                                                      |
| Safety checks                                 | `tests/test_safety.py` and safety implementation                                           |
| Common generation interface                   | `src/avatar_system/generation/base.py`                                                     |
| Kaggle generation route                       | `src/avatar_system/generation/kaggle.py`                                                   |
| Kaggle dataset update before worker execution | `src/avatar_system/generation/kaggle.py`                                                   |
| Output validation                             | `tests/test_validate.py` and validation implementation                                     |
| Output evaluation                             | `tests/test_evalaution.py` and evaluation implementation                                   |
| Manifest generation                           | `src/avatar_system/generation/manifest.py` and `tests/test_manifest.py`                    |
| End-to-end workflow                           | `tests/test_end_to_end.py`                                                                 |
| Automated tests                               | `tests/`                                                                                   |
| Six-avatar matrix                             | `examples/avatar_011.json`–`examples/avatar_016.json`, `outputs/job_009`–`outputs/job_014` |
| Controlled attribute matrix                   | `examples/avatar_017.json`–`examples/avatar_020.json`                                      |
| Benchmark measurements                        | `avatar benchmark --job <job_id>` and saved benchmark record                               |
| Deterministic seeds                           | job/result metadata and `src/avatar_system/generation/kaggle.py`                           |
| Kaggle T4 benchmark                           | `outputs/job_007/`                                                                         |

## Reproduction Commands

``` powershell
avatar prepare --spec examples/avatar_011.json
avatar generate --job <job_id>
avatar validate --job <job_id>
avatar evaluate --job <job_id>
avatar benchmark --job <job_id>
pytest -q
```

## Evidence to Retain

For each selected run, retain:

``` text
jobs/<job_id>/job.json
outputs/<job_id>/avatar-output/
```

Also retain the Kaggle worker source/notebook, worker logs, dataset
input job, downloaded outputs, environment/lock information, and exact
model revision where applicable.
