# hot_fair_utilities

Utilities for AI-assisted mapping workflows in fAIr.

## Prerequisites

- Linux with GDAL system libraries available
- [uv](https://docs.astral.sh/uv/)

## Local installation

```bash
git clone https://github.com/hotosm/fAIr-utilities.git
cd fAIr-utilities
uv sync --group dev
```

## Run sample workflows

```bash
just run ramp
just run yolo
```

## Docker workflow

```bash
docker build -t fairutils .
docker run -it --rm --gpus=all -p 8888:8888 fairutils
```

Use `bash` as the container command if you want an interactive shell.

## Notebook test workflow

Run [Package_Test.ipynb](./Package_Test.ipynb) to validate the package workflow on the sample dataset.

## Development notes

Follow [docs/Version_control.md](./docs/Version_control.md) for release and versioning guidance.
