set shell := ["bash", "-cu"]

setup:
	uv sync --group dev
	uv run --no-sync pre-commit install

lint:
	uv sync --group lint
	uv run --no-sync ruff check --fix .
	uv run --no-sync ruff format .

check:
	uv sync --group lint
	uv run --no-sync ruff check --fix .
	uv run --no-sync ruff format .
	uv run --no-sync pre-commit run --all-files

test:
	uv sync --group test
	uv run --no-sync pytest


[private]
_ensure-ramp-assets:
	#!/usr/bin/env bash
	set -euo pipefail

	if [[ ! -d ramp-data/baseline/checkpoint.tf ]]; then
		mkdir -p ramp-data/baseline
		wget -q https://api-prod.fair.hotosm.org/api/v1/workspace/download/ramp/baseline.zip -O baseline.zip
		unzip -oq baseline.zip -d ramp-data/baseline
		rm -f baseline.zip
	fi

[private]
_run-ramp extra:
	uv python install 3.11
	uv sync --python 3.11 --extra {{extra}} --group test
	RAMP_HOME="$PWD" uv run --no-sync --python 3.11 --extra {{extra}} python test_ramp.py

ramp:
	just _ensure-ramp-assets
	just _run-ramp ramp

ramp-gpu:
	just _ensure-ramp-assets
	just _run-ramp ramp-gpu

yolo:
	uv sync --extra yolo --group test
	uv run --no-sync --extra yolo python test_yolo.py

run target='':
	#!/usr/bin/env bash
	set -euo pipefail

	case "{{target}}" in
		""|ramp)
			just ramp
			;;
		ramp-gpu)
			just ramp-gpu
			;;
		yolo)
			just yolo
			;;
		*)
			echo "Usage: just run <ramp|ramp-gpu|yolo>"
			exit 1
			;;
	esac