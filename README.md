# hot_fair_utilities

Utilities for AI-assisted mapping workflows in [fAIr](https://github.com/hotosm/fAIr) — the Humanitarian OpenStreetMap Team's AI-assisted mapping platform.

This package provides training, inference, and preprocessing tools for building detection models (RAMP and YOLOv8) used in humanitarian mapping — identifying buildings from satellite imagery to support disaster response, development planning, and community mapping.

## Prerequisites

- Python 3.10+
- GDAL system libraries (see OS-specific instructions below)
- [uv](https://docs.astral.sh/uv/) — fast Python package manager
- [just](https://github.com/casey/just) — command runner

## Local installation

```bash
just setup
```

### Installing GDAL

**macOS:**
```bash
brew install gdal
```

**Debian / Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev
```

**Windows (WSL recommended):**
```bash
# Inside WSL (Ubuntu)
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev
```

> **Note:** Native Windows is not officially supported due to GDAL dependencies. Use WSL or Docker instead.

## Run sample workflows

```bash
just run ramp    # RAMP building detection model
just run yolo    # YOLOv8 segmentation model
```

`just run ramp` downloads the baseline checkpoint into `ramp-data/baseline` when needed.

Ramp training exports the selected best checkpoint as `.h5`, and inference uses that exported checkpoint directly.

## Validation

Run all quality gates and integration checks:

```bash
just check       # lint + format check
just test-all    # integration tests
```

## Docker images

Modes and image tags:

| Model | Device | Image tag | Build command |
|---|---|---|---|
| RAMP | CPU | `fair-utilities:ramp` | `docker build -f docker/Dockerfile.ramp --build-arg FLAVOR=cpu -t fair-utilities:ramp .` |
| RAMP | GPU | `fair-utilities:ramp-gpu` | `docker build -f docker/Dockerfile.ramp --build-arg FLAVOR=gpu -t fair-utilities:ramp-gpu .` |
| YOLOv8 | CPU | `fair-utilities:yolo` | `docker build -f docker/Dockerfile.yolo --build-arg FLAVOR=cpu -t fair-utilities:yolo .` |
| YOLOv8 | GPU | `fair-utilities:yolo-gpu` | `docker build -f docker/Dockerfile.yolo --build-arg FLAVOR=gpu -t fair-utilities:yolo-gpu .` |

## Project structure

```
hot_fair_utilities/
├── training/          # Model training pipelines (RAMP + YOLO)
├── inference/         # Run predictions on satellite imagery
├── preprocessing/     # Prepare training data from OSM labels
├── postprocessing/    # Clean up model outputs
├── model/             # Model loading and configuration
└── utils.py           # Shared utilities
```

## Notebook test workflow

Run [Package_Test.ipynb](./Package_Test.ipynb) to validate the package workflow on the sample dataset.

## Benchmark docs

See [docs/benchmark/sample-datasets.md](./docs/benchmark/sample-datasets.md) for benchmark dataset details.

## Contributing

1. Fork the repo and create a branch from `master`
2. Install dev dependencies: `just setup`
3. Run lint and tests: `just check && just test-all`
4. Submit a PR

See [docs/Version_control.md](./docs/Version_control.md) for release and versioning guidance.
