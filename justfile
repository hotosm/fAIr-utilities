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

run target:
	#!/usr/bin/env bash
	set -euo pipefail

	if [[ "{{target}}" == "ramp" ]]; then
		if [[ ! -d ramp-code ]]; then
			git clone https://github.com/kshitijrajsharma/ramp-code-fAIr.git ramp-code
		fi

		if [[ ! -d ramp-code/ramp/checkpoint.tf ]]; then
			wget -q https://api-prod.fair.hotosm.org/api/v1/workspace/download/ramp/baseline.zip -O baseline.zip
			unzip -oq baseline.zip -d ramp-code/ramp
			rm -f baseline.zip
		fi

		uv python install 3.11
		uv sync --python 3.11 --extra ramp --group test
		RAMP_HOME="$PWD" uv run --no-sync --python 3.11 --extra ramp python test_ramp.py
	elif [[ "{{target}}" == "yolo" ]]; then
		uv sync --extra yolo --group test
		uv run --no-sync --extra yolo python test_yolo.py
	else
		echo "Usage: just run <ramp|yolo>"
		exit 1
	fi