set shell := ["bash", "-cu"]

setup:
	uv sync --group dev
	uv run --no-sync pre-commit install

lint:
	uv sync --group lint
	uv run --no-sync ruff check .
	uv run --no-sync ruff format --check .

format:
	uv sync --group lint
	uv run --no-sync ruff check --fix .
	uv run --no-sync ruff format .

typecheck:
	uv sync --group typecheck
	uv run --no-sync ty check hot_fair_utilities/

test:
	uv sync --group test
	uv run --no-sync bash -c 'pytest --ignore test_ramp.py --ignore test_yolo.py; code=$?; if [[ "$code" -eq 5 ]]; then echo "No unit tests collected; skipping base pytest suite."; exit 0; fi; exit "$code"'

check: lint typecheck test

[private]
_ensure-ramp-assets:
	#!/usr/bin/env bash
	set -euo pipefail

	if [[ ! -d ramp-data/baseline/checkpoint.tf ]]; then
		mkdir -p ramp-data/baseline
		if command -v wget >/dev/null; then
			wget -q https://api-prod.fair.hotosm.org/api/v1/workspace/download/ramp/baseline.zip -O baseline.zip
		else
			curl -fsSL https://api-prod.fair.hotosm.org/api/v1/workspace/download/ramp/baseline.zip -o baseline.zip
		fi
		unzip -oq baseline.zip -d ramp-data/baseline
		rm -f baseline.zip
	fi

[private]
_run-ramp extra:
	uv python install 3.11
	uv sync --python 3.11 --extra {{extra}} --extra predict --group test
	RAMP_HOME="$PWD" uv run --no-sync --python 3.11 --extra {{extra}} --extra predict python test_ramp.py

ramp:
	just _ensure-ramp-assets
	just _run-ramp ramp

ramp-gpu:
	just _ensure-ramp-assets
	just _run-ramp ramp-gpu

yolo:
	uv sync --extra yolo-cpu --extra predict --group test
	uv run --no-sync --extra yolo-cpu --extra predict python test_yolo.py

test-all:
	just test
	just ramp
	just yolo

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
