#!/usr/bin/env python3
"""Validate Genesis Protocol asset manifests without third-party packages."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_TOP = {"schema_version", "project", "naming_convention", "export_settings", "palette", "assets"}
REQUIRED_ASSET = {"id", "name", "category", "variant", "LOD", "version", "formats", "size_bytes", "polycount", "texture_resolutions", "dependencies", "readme_path"}
ID_RE = re.compile(r"^[a-z]+_[a-z0-9]+_[a-z0-9]+_LOD[0-2]_v\d{2}$|^[a-z]+_[a-z0-9]+_[a-z0-9]+_[a-z0-9]+_v\d{2}$")
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
VALID_LOD = {"LOD0", "LOD1", "LOD2", "NA"}
VALID_CATEGORY = {"world", "biome", "character", "npc", "enemy", "boss", "prop", "tool", "ui", "vfx", "audio", "scene"}


def fail(message: str) -> None:
    print(f"manifest validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    manifest_path = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/manifest/asset_manifest.json")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    missing = REQUIRED_TOP - data.keys()
    if missing:
        fail(f"missing top-level fields: {sorted(missing)}")
    if data["naming_convention"] != "category_assetname_variant_LOD_version":
        fail("unexpected naming convention")
    if len(data["palette"]) != 6:
        fail("palette must contain exactly 6 colors")
    for color in data["palette"]:
        if not HEX_RE.match(color.get("hex", "")):
            fail(f"invalid palette hex: {color}")

    ids: set[str] = set()
    for asset in data["assets"]:
        missing_asset = REQUIRED_ASSET - asset.keys()
        if missing_asset:
            fail(f"{asset.get('id', '<unknown>')} missing fields: {sorted(missing_asset)}")
        if asset["id"] in ids:
            fail(f"duplicate asset id: {asset['id']}")
        ids.add(asset["id"])
        if not ID_RE.match(asset["id"]):
            fail(f"asset id does not match convention: {asset['id']}")
        if asset["LOD"] not in VALID_LOD:
            fail(f"invalid LOD for {asset['id']}: {asset['LOD']}")
        if asset["category"] not in VALID_CATEGORY:
            fail(f"invalid category for {asset['id']}: {asset['category']}")
        if not isinstance(asset["formats"], list) or not asset["formats"]:
            fail(f"formats must be non-empty for {asset['id']}")
        if asset["polycount"] < 0 or asset["size_bytes"] < 0:
            fail(f"negative budget field for {asset['id']}")

    print(f"validated {len(ids)} assets and {len(data['palette'])} palette colors in {manifest_path}")


if __name__ == "__main__":
    main()
  
