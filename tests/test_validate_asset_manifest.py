import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_asset_manifest.py"
MANIFEST = ROOT / "assets" / "manifest" / "asset_manifest.json"


def run_validator(payload):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(payload, fh)
        path = Path(fh.name)
    try:
        return subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True, check=False)
    finally:
        path.unlink(missing_ok=True)


def test_manifest_passes_validator():
    result = subprocess.run([sys.executable, str(VALIDATOR), str(MANIFEST)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "validated" in result.stdout


def test_validator_rejects_duplicate_ids():
    data = json.loads(MANIFEST.read_text())
    data["assets"].append(copy.deepcopy(data["assets"][0]))
    result = run_validator(data)
    assert result.returncode == 1
    assert "duplicate asset id" in result.stderr


def test_validator_rejects_bad_palette_hex():
    data = json.loads(MANIFEST.read_text())
    data["palette"][0]["hex"] = "171A1C"
    result = run_validator(data)
    assert result.returncode == 1
    assert "invalid palette hex" in result.stderr


def test_validator_rejects_bad_lod():
    data = json.loads(MANIFEST.read_text())
    data["assets"][0]["LOD"] = "LOD9"
    result = run_validator(data)
    assert result.returncode == 1
    assert "invalid LOD" in result.stderr
  
