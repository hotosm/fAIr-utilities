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

## Docker workflow

Build:

```bash
for model in ramp yolo; do
	for flavor in cpu gpu; do
		if [ "$flavor" = "cpu" ]; then
			tag="fair-utilities:${model}"
		else
			tag="fair-utilities:${model}-gpu"
		fi
		docker build -f "docker/Dockerfile.${model}" --build-arg "FLAVOR=${flavor}" -t "$tag" .
	done
done
```

Run:

```bash
docker run --rm fair-utilities:ramp
docker run --rm fair-utilities:yolo
docker run --rm --gpus all fair-utilities:ramp-gpu
docker run --rm --gpus all fair-utilities:yolo-gpu
```

Notes: two Dockerfiles only (`ramp`, `yolo`), GPU requires NVIDIA Container Toolkit, Ramp image fetches baseline checkpoint at build time, and YOLO uses flavor-specific torch extras (`yolo-cpu`, `yolo-gpu`) with pinned PyTorch indexes.

## Notebook test workflow

Run [Package_Test.ipynb](./Package_Test.ipynb) to validate the package workflow on the sample dataset.

## Benchmark docs

See [docs/benchmark/sample-datasets.md](./docs/benchmark/sample-datasets.md) for benchmark dataset details.

## Development notes

Follow [docs/Version_control.md](./docs/Version_control.md) for release and versioning guidance.
