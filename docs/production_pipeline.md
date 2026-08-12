# Production Pipeline Entry Point

The canonical production asset pipeline lives at [`docs/assets/production_pipeline.md`](assets/production_pipeline.md). This entry point exists so PR descriptions, CI logs, and external documentation can link to `docs/production_pipeline.md` without drifting from the canonical asset-pipeline document.

Required CI checks:

```bash
python3 -m json.tool assets/manifest/asset_manifest.json
python3 tools/validate_asset_manifest.py assets/manifest/asset_manifest.json
python3 tools/validate_gameplay_data.py
python3 tools/build_asset_bundle.py --output build/GenesisProtocol_MetadataBundle_v01.tar.gz
python3 -m pytest tests/test_validate_asset_manifest.py tests/test_validate_gameplay_data.py
```
