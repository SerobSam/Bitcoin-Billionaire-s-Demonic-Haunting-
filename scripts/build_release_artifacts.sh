#!/usr/bin/env bash
set -euo pipefail

# Builds release APK and AAB artifacts for Genesis Protocol.
# Optional signing environment variables:
#   GENESIS_UPLOAD_STORE_FILE=/absolute/path/upload-keystore.jks
#   GENESIS_UPLOAD_STORE_PASSWORD=...
#   GENESIS_UPLOAD_KEY_ALIAS=upload
#   GENESIS_UPLOAD_KEY_PASSWORD=...

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${DIST_DIR:-$ROOT_DIR/dist/release}"
JAVA_HOME="${JAVA_HOME:-/root/.local/share/mise/installs/java/17.0.2}"
ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}"
ANDROID_HOME="${ANDROID_HOME:-$ANDROID_SDK_ROOT}"
ANDROID_NDK_HOME="${ANDROID_NDK_HOME:-$ANDROID_SDK_ROOT/ndk/27.1.12516514}"

export JAVA_HOME ANDROID_SDK_ROOT ANDROID_HOME ANDROID_NDK_HOME
export PATH="$ANDROID_SDK_ROOT/cmdline-tools/tools/bin:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/build-tools/36.0.0:$PATH"

missing=0
if [[ ! -x "$JAVA_HOME/bin/java" ]]; then
  echo "Missing Java 17 at JAVA_HOME=$JAVA_HOME" >&2
  missing=1
fi
if [[ ! -d "$ANDROID_SDK_ROOT/platforms/android-36" ]]; then
  echo "Missing Android SDK platform android-36 under $ANDROID_SDK_ROOT" >&2
  missing=1
fi
if [[ ! -d "$ANDROID_NDK_HOME" ]]; then
  echo "Missing Android NDK at $ANDROID_NDK_HOME" >&2
  missing=1
fi
if [[ "$missing" -ne 0 ]]; then
  cat >&2 <<HELP
Install prerequisites first:
  scripts/setup_android_build_env.sh

Then re-run:
  scripts/build_release_artifacts.sh
HELP
  exit 1
fi

cd "$ROOT_DIR"
gradle :app:assembleRelease :app:bundleRelease

mkdir -p "$DIST_DIR"
cp app/build/outputs/apk/release/app-release.apk "$DIST_DIR/GenesisProtocol-release.apk"
cp app/build/outputs/bundle/release/app-release.aab "$DIST_DIR/GenesisProtocol-release.aab"

cat <<DONE
Release artifacts built:
  $DIST_DIR/GenesisProtocol-release.apk
  $DIST_DIR/GenesisProtocol-release.aab
DONE
