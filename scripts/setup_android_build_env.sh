#!/usr/bin/env bash
set -euo pipefail

# Installs the Android command-line SDK components required to build Genesis Protocol.
# Ubuntu usage:
#   sudo scripts/setup_android_build_env.sh --install-jdk
#   scripts/setup_android_build_env.sh

COMPILE_SDK="${COMPILE_SDK:-36}"
BUILD_TOOLS_VERSION="${BUILD_TOOLS_VERSION:-36.0.0}"
NDK_VERSION="${NDK_VERSION:-27.1.12516514}"
CMAKE_VERSION="${CMAKE_VERSION:-3.22.1}"
CMDLINE_TOOLS_ZIP="${CMDLINE_TOOLS_ZIP:-commandlinetools-linux-9477386_latest.zip}"
CMDLINE_TOOLS_URL="${CMDLINE_TOOLS_URL:-https://dl.google.com/android/repository/${CMDLINE_TOOLS_ZIP}}"
CMDLINE_TOOLS_ARCHIVE="${CMDLINE_TOOLS_ARCHIVE:-}"
ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-${HOME}/Android/Sdk}"
INSTALL_JDK="false"

for arg in "$@"; do
  case "$arg" in
    --install-jdk) INSTALL_JDK="true" ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [[ "$INSTALL_JDK" == "true" ]]; then
  if [[ "$(id -u)" -ne 0 ]]; then
    echo "--install-jdk requires sudo/root so apt-get can install openjdk-17-jdk." >&2
    exit 1
  fi
  apt-get update
  apt-get install -y openjdk-17-jdk unzip wget ca-certificates
fi

if ! command -v java >/dev/null 2>&1; then
  echo "java is not installed. Run: sudo $0 --install-jdk" >&2
  exit 1
fi
if ! command -v javac >/dev/null 2>&1; then
  echo "javac is not installed. Run: sudo $0 --install-jdk" >&2
  exit 1
fi

mkdir -p "$ANDROID_SDK_ROOT/cmdline-tools"
cd "$ANDROID_SDK_ROOT"

if [[ ! -x "$ANDROID_SDK_ROOT/cmdline-tools/tools/bin/sdkmanager" ]]; then
  rm -rf "$ANDROID_SDK_ROOT/cmdline-tools/latest-tmp" "$ANDROID_SDK_ROOT/cmdline-tools/tools" "$CMDLINE_TOOLS_ZIP"
  if [[ -n "$CMDLINE_TOOLS_ARCHIVE" ]]; then
    if [[ ! -f "$CMDLINE_TOOLS_ARCHIVE" ]]; then
      echo "CMDLINE_TOOLS_ARCHIVE does not exist: $CMDLINE_TOOLS_ARCHIVE" >&2
      exit 1
    fi
    cp "$CMDLINE_TOOLS_ARCHIVE" "$CMDLINE_TOOLS_ZIP"
  else
    if ! wget -O "$CMDLINE_TOOLS_ZIP" "$CMDLINE_TOOLS_URL"; then
      cat >&2 <<DOWNLOAD_HELP
Failed to download Android command-line tools from:
  $CMDLINE_TOOLS_URL

If this environment blocks dl.google.com, download the archive on a machine with
network access and re-run with:
  CMDLINE_TOOLS_ARCHIVE=/path/to/$CMDLINE_TOOLS_ZIP $0
DOWNLOAD_HELP
      exit 1
    fi
  fi
  unzip -q "$CMDLINE_TOOLS_ZIP" -d "$ANDROID_SDK_ROOT/cmdline-tools/latest-tmp"
  mkdir -p "$ANDROID_SDK_ROOT/cmdline-tools/tools"
  shopt -s dotglob
  mv "$ANDROID_SDK_ROOT/cmdline-tools/latest-tmp/cmdline-tools"/* "$ANDROID_SDK_ROOT/cmdline-tools/tools/"
  shopt -u dotglob
  rm -rf "$ANDROID_SDK_ROOT/cmdline-tools/latest-tmp" "$CMDLINE_TOOLS_ZIP"
fi

export ANDROID_SDK_ROOT
export ANDROID_HOME="$ANDROID_SDK_ROOT"
export ANDROID_NDK_HOME="$ANDROID_SDK_ROOT/ndk/$NDK_VERSION"
export PATH="$ANDROID_SDK_ROOT/cmdline-tools/tools/bin:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/build-tools/$BUILD_TOOLS_VERSION:$PATH"

yes | sdkmanager --licenses >/dev/null
sdkmanager \
  "platforms;android-${COMPILE_SDK}" \
  "platform-tools" \
  "build-tools;${BUILD_TOOLS_VERSION}" \
  "ndk;${NDK_VERSION}" \
  "cmake;${CMAKE_VERSION}"

cat <<ENV

Android build environment is ready.
Add these exports to your shell profile if needed:
export ANDROID_SDK_ROOT="$ANDROID_SDK_ROOT"
export ANDROID_HOME="$ANDROID_SDK_ROOT"
export ANDROID_NDK_HOME="$ANDROID_SDK_ROOT/ndk/$NDK_VERSION"
export PATH="$ANDROID_SDK_ROOT/cmdline-tools/tools/bin:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/build-tools/$BUILD_TOOLS_VERSION:\$PATH"

Verify with:
java -version
javac -version
sdkmanager --list_installed

Build with:
gradle :app:assembleRelease
gradle :app:bundleRelease
ENV
