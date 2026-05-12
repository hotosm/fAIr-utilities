#!/usr/bin/env python3
"""Real-data repro for YOLO label writing (write_yolo_file) normalization issues.

This runs ``hot_fair_utilities.preprocess`` on a raw input folder (PNG chips + labels.geojson),
producing a ``preprocessed`` directory with paired:
  - chips/*.tif
  - labels/*.geojson

Then it calls ``hot_fair_utilities.preprocessing.yolo_v8.utils.write_yolo_file`` on one
generated chip and prints the resulting YOLO label line.

Run from the fAIr-utilities repo root::

    uv run python repro_write_yolo_file.py --input-dir ramp-data/sample_2/input --work-dir E:/tmp/repro_yolo

If the printed YOLO line has many coordinates stuck at 0.0 or 1.0, labels are collapsing.
"""

from __future__ import annotations

import json
import tempfile
import argparse
from pathlib import Path

from hot_fair_utilities.preprocessing.yolo_v8.utils import write_yolo_file


def _print_yolo_txt(txt_path: Path) -> None:
    text = txt_path.read_text(encoding="utf-8").strip() if txt_path.exists() else ""
    print("--- write_yolo_file output ---")
    print(text or "(empty file or missing)")
    print("--- path ---")
    print(txt_path)
    nums = [float(x) for x in text.replace("\n", " ").split()[1:]] if text else []
    if nums:
        print(f"--- stats (normalized coords): min={min(nums):.6f} max={max(nums):.6f} count={len(nums)} ---")


def _run_real(input_dir: Path, root: Path, epsg: int) -> None:
    from hot_fair_utilities import preprocess as hf_preprocess

    if not (input_dir / "labels.geojson").is_file():
        raise FileNotFoundError(f"Expected labels.geojson under input_dir: {input_dir}")

    # preprocess() expects raw layout: <input_dir> contains labels.geojson and chips (usually PNGs).
    # It will create: <output>/chips/*.tif and <output>/labels/*.geojson (per-tile).
    pre = root / "preprocessed_yolo_test"
    yolo_out = root / "yolo_out"
    pre.mkdir(parents=True, exist_ok=True)
    yolo_out.mkdir(parents=True, exist_ok=True)

    hf_preprocess(
        input_path=str(input_dir),
        output_path=str(pre),
        rasterize=True,
        rasterize_options=["binary"],
        georeference_images=True,
        multimasks=False,
        epsg=epsg,
    )

    chips_dir = pre / "chips"
    labels_dir = pre / "labels"
    tif_paths = sorted(chips_dir.glob("*.tif"))
    if not tif_paths:
        raise RuntimeError(f"No chips were produced at {chips_dir}. Is the input missing PNG chips?")

    chip = tif_paths[0]
    expected_label = labels_dir / f"{chip.stem}.geojson"
    if not expected_label.is_file():
        raise RuntimeError(f"Missing expected per-chip label: {expected_label}")

    write_yolo_file(str(chip), "train", str(yolo_out))
    _print_yolo_txt(yolo_out / "labels" / "train" / f"{chip.stem}.txt")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Raw input directory containing labels.geojson (+ PNG chips). Runs preprocess then write_yolo_file.",
    )
    ap.add_argument(
        "--work-dir",
        type=str,
        default="",
        help="Optional work directory. Defaults to a temp folder.",
    )
    ap.add_argument(
        "--epsg",
        type=int,
        default=3857,
        choices=[3857, 4326],
        help="EPSG passed to hot_fair_utilities.preprocess (default: 3857).",
    )
    args = ap.parse_args()

    root = Path(args.work_dir) if args.work_dir else Path(tempfile.mkdtemp(prefix="repro_yolo_labels_"))
    root.mkdir(parents=True, exist_ok=True)

    _run_real(Path(args.input_dir), root, epsg=args.epsg)

    print("\nWorkdir (delete manually if you want to inspect):", root)
    # Uncomment to auto-cleanup:
    # shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
