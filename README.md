# hot_fair_utilities

Utilities for AI-assisted mapping workflows in fAIr.

## Prerequisites

- Linux with GDAL system libraries available
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just)

## Local installation

```bash
git clone https://github.com/hotosm/fAIr-utilities.git
cd fAIr-utilities
just setup
```

## Run sample workflows

```bash
just run ramp
just run yolo
```

## Docker workflow

```bash
TBF
```

Use `bash` as the container command if you want an interactive shell.

## Notebook test workflow

Run [Package_Test.ipynb](./Package_Test.ipynb) to validate the package workflow on the sample dataset.

## Benchmark docs

See [docs/benchmark/sample-datasets.md](./docs/benchmark/sample-datasets.md) for benchmark dataset details.

## Development notes

Follow [docs/Version_control.md](./docs/Version_control.md) for release and versioning guidance.
