#!/usr/bin/env python3
"""Create a deterministic Genesis Protocol asset export zip."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

INCLUDE_DIRS = [
    "00_styleguide", "01_world", "02_biomes", "03_characters", "04_props", "assets/gameplay",
    "05_tools", "06_ui", "07_vfx", "08_audio_refs", "09_scenes", "10_final_3d_engine_package", "11_full_game_build", "12_finished_game", "manifest", "assets/manifest",
]
INCLUDE_FILES = ["docs/assets/production_ready_art_asset_pipeline.md", "docs/assets/production_pipeline.md", "docs/assets/complete_3d_asset_package_spec.json", "docs/assets/final_3d_engine_package_spec.json"]


def iter_files(root: Path):
    for dirname in INCLUDE_DIRS:
        base = root / dirname
        if base.exists():
            yield from sorted(p for p in base.rglob("*") if p.is_file())
    for filename in INCLUDE_FILES:
        path = root / filename
        if path.exists():
            yield path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", default=".", help="repository root")
    parser.add_argument("--out", default="build/genesis_asset_export.zip", help="zip output path")
    args = parser.parse_args()

    root = Path(args.src).resolve()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in iter_files(root):
            arcname = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(arcname)
            info.date_time = (2026, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())

    count = sum(1 for _ in iter_files(root))
    print(f"wrote {out} with {count} files")


if __name__ == "__main__":
    main()
