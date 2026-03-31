# hot_fair_utilities

Utilities for AI-assisted mapping workflows in fAIr.

## Prerequisites

- GDAL system libraries available (Linux or macOS)
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just)

## Local installation

```bash
just setup
```

If GDAL is missing on macOS, install it with Homebrew:

```bash
brew install gdal
```

If GDAL is missing on Debian or Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev
```

## Run sample workflows

```bash
just run ramp
just run yolo
```

`just run ramp` downloads the baseline checkpoint into `ramp-data/baseline` when needed. 

Ramp training exports the selected best checkpoint as `.h5`, and inference uses that exported checkpoint directly.

## Validation

Run all quality gates and integration checks:

```bash
just check
just test-all
```

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
