.PHONY: all build test validate validate-json validate-assets validate-gameplay bundle clean android-release

PYTHON ?= python3
BUNDLE_OUTPUT ?= build/GenesisProtocol_MetadataBundle_v01.tar.gz

all: build

# Default CI-safe build. The GitHub C/C++ workflow for this repository invokes
# make from the repository root on Ubuntu without an Android SDK. Keep this
# target deterministic and SDK-independent so metadata, docs, and tooling are
# validated even when Android release artifacts are built in a separate job.
build: validate test bundle

validate: validate-json validate-assets validate-gameplay

validate-json:
	$(PYTHON) -m json.tool assets/manifest/asset_manifest.json >/dev/null
	$(PYTHON) -m json.tool assets/destructibility/destructible_state_machine.json >/dev/null
	$(PYTHON) -m json.tool assets/world/streaming_grid_sample.json >/dev/null
	$(PYTHON) -m json.tool assets/gameplay/classes.json >/dev/null
	$(PYTHON) -m json.tool assets/gameplay/loot_tiers.json >/dev/null
	$(PYTHON) -m json.tool assets/gameplay/merkle_rules.json >/dev/null
	$(PYTHON) -m json.tool schemas/asset/manifest.schema.json >/dev/null

validate-assets:
	$(PYTHON) tools/validate_asset_manifest.py assets/manifest/asset_manifest.json

validate-gameplay:
	$(PYTHON) tools/validate_gameplay_data.py

test:
	$(PYTHON) -m pytest tests/test_validate_asset_manifest.py tests/test_validate_gameplay_data.py

bundle:
	$(PYTHON) tools/build_asset_bundle.py --output $(BUNDLE_OUTPUT)

# Android release output requires Android SDK/NDK and, for Play upload,
# GENESIS_UPLOAD_* signing variables. This target is intentionally separate
# from the default CI-safe build target.
android-release:
	scripts/build_release_artifacts.sh

clean:
	rm -rf build dist .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
