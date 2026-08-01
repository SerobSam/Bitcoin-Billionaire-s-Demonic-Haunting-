#!/usr/bin/env python3
"""Build a deterministic Genesis Protocol engine-import bundle.

The repository does not store large binary art exports. This packager collects the
machine-readable metadata, production documentation, and runtime JSON configs that
engine/content tooling needs before large FBX/GLTF/texture files are attached by CI.
"""
from __future__ import annotations

import argparse
import json
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INCLUDE = [
    "assets/manifest/asset_manifest.json",
    "assets/destructibility/destructible_state_machine.json",
    "assets/world/streaming_grid_sample.json",
    "schemas/asset_manifest.schema.json",
    "docs/genesis_protocol_complete_spec.md",
    "docs/assets/production_pipeline.md",
    "docs/production_pipeline.md",
]


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def copy_file(src: Path, dest_root: Path) -> None:
    rel = src.relative_to(ROOT)
    dest = dest_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def write_bundle_index(manifest: dict, staging: Path, bundle_name: str) -> None:
    index = {
        "bundle_name": bundle_name,
        "project": manifest["project"],
        "schema_version": manifest["schema_version"],
        "asset_count": len(manifest["assets"]),
        "palette": manifest["palette"],
        "included_metadata": DEFAULT_INCLUDE,
    }
    (staging / "bundle_index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")


def make_archive(staging: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:gz", format=tarfile.PAX_FORMAT) as tar:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                tar.add(path, arcname=path.relative_to(staging))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Genesis Protocol metadata bundle")
    parser.add_argument("--output", default="build/GenesisProtocol_MetadataBundle_v01.tar.gz")
    parser.add_argument("--staging", default="build/asset_bundle_staging")
    args = parser.parse_args()

    staging = ROOT / args.staging
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    manifest_path = ROOT / "assets/manifest/asset_manifest.json"
    manifest = load_manifest(manifest_path)
    for rel in DEFAULT_INCLUDE:
        copy_file(ROOT / rel, staging)
    write_bundle_index(manifest, staging, Path(args.output).name)
    make_archive(staging, ROOT / args.output)
    print(f"wrote {ROOT / args.output}")


if __name__ == "__main__":
    main()
  
