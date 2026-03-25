# hot_fair_utilities

Utilities for AI-assisted mapping workflows in fAIr.

## Prerequisites

- Linux with GDAL system libraries available
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just)

## Local installation

```bash
just setup
```

## Run sample workflows

```bash
just run ramp
just run yolo
```

`just run ramp` downloads the baseline checkpoint into `ramp-data/baseline` when needed. 

## Docker images

Modes and image tags:

- `ramp` + `cpu` -> `fair-utilities:ramp`
- `ramp` + `gpu` -> `fair-utilities:ramp-gpu`
- `yolo` + `cpu` -> `fair-utilities:yolo`
- `yolo` + `gpu` -> `fair-utilities:yolo-gpu`

Build commands:

```bash
docker build -f docker/Dockerfile.ramp --build-arg FLAVOR=cpu -t fair-utilities:ramp .
docker build -f docker/Dockerfile.ramp --build-arg FLAVOR=gpu -t fair-utilities:ramp-gpu .
docker build -f docker/Dockerfile.yolo --build-arg FLAVOR=cpu -t fair-utilities:yolo .
docker build -f docker/Dockerfile.yolo --build-arg FLAVOR=gpu -t fair-utilities:yolo-gpu .
```

## Notebook test workflow

Run [Package_Test.ipynb](./Package_Test.ipynb) to validate the package workflow on the sample dataset.

## Benchmark docs

See [docs/benchmark/sample-datasets.md](./docs/benchmark/sample-datasets.md) for benchmark dataset details.

## Development notes

Follow [docs/Version_control.md](./docs/Version_control.md) for release and versioning guidance.
