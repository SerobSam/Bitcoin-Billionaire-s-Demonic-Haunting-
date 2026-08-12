# Android Build Setup on Ubuntu/Linux

This project targets Android with Kotlin, Jetpack Compose, a native C++ engine, and Vulkan. The commands below install the Android SDK pieces that match `app/build.gradle.kts`: compile SDK 36, build tools 36.0.0, NDK 27.1.12516514, and CMake 3.22.1.

## One-command setup

```bash
sudo scripts/setup_android_build_env.sh --install-jdk
scripts/setup_android_build_env.sh
```

If OpenJDK 17 is already installed, run only the second command.

## Manual setup

```bash
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk unzip wget ca-certificates
java -version
javac -version

mkdir -p "$HOME/Android/Sdk"
cd "$HOME/Android/Sdk"
wget -O commandlinetools-linux-9477386_latest.zip \
  https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip -d cmdline-tools-tmp
mkdir -p cmdline-tools/tools
mv cmdline-tools-tmp/cmdline-tools/* cmdline-tools/tools/
rm -rf cmdline-tools-tmp commandlinetools-linux-9477386_latest.zip

export ANDROID_SDK_ROOT="$HOME/Android/Sdk"
export ANDROID_HOME="$HOME/Android/Sdk"
export ANDROID_NDK_HOME="$HOME/Android/Sdk/ndk/27.1.12516514"
export PATH="$ANDROID_SDK_ROOT/cmdline-tools/tools/bin:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/build-tools/36.0.0:$PATH"

yes | sdkmanager --licenses
sdkmanager \
  "platforms;android-36" \
  "platform-tools" \
  "build-tools;36.0.0" \
  "ndk;27.1.12516514" \
  "cmake;3.22.1"
```

> Avoid smart quotes in `sdkmanager` package names. Use `"ndk;27.1.12516514"` and `"cmake;3.22.1"` exactly.


## Network-restricted environments

If `dl.google.com` is blocked by a corporate proxy or container policy, pre-download `commandlinetools-linux-9477386_latest.zip` on another machine, copy it into the workspace, and run:

```bash
ANDROID_SDK_ROOT=/root/Android/Sdk \
CMDLINE_TOOLS_ARCHIVE=/path/to/commandlinetools-linux-9477386_latest.zip \
scripts/setup_android_build_env.sh
```

The script will use the local archive instead of calling `wget`, then install `platforms;android-36`, `build-tools;36.0.0`, `ndk;27.1.12516514`, and `cmake;3.22.1` through `sdkmanager`.

## Build APK and AAB

From the repository root:

```bash
gradle :app:assembleRelease
gradle :app:bundleRelease
find . -name "app-release.apk" -type f
find . -name "app-release.aab" -type f
```

The explicit `:app:` prefix avoids ambiguity in multi-module Gradle projects.


## Signed Play Store release artifacts

For Google Play upload, create or provide an upload keystore outside the repository and export the signing variables before building:

```bash
export GENESIS_UPLOAD_STORE_FILE="$HOME/keystores/genesis-upload.jks"
export GENESIS_UPLOAD_STORE_PASSWORD="<store-password>"
export GENESIS_UPLOAD_KEY_ALIAS="upload"
export GENESIS_UPLOAD_KEY_PASSWORD="<key-password>"
scripts/build_release_artifacts.sh
```

The helper copies final artifacts to:

```text
dist/release/GenesisProtocol-release.apk
dist/release/GenesisProtocol-release.aab
```

Do not commit keystores or passwords. If these variables are omitted, Gradle may produce unsigned release outputs depending on the local Android Gradle Plugin behavior, but Google Play upload requires a signed AAB or Play App Signing enrollment.

## Verify SDK environment

```bash
ls -la "$ANDROID_SDK_ROOT"
echo "$ANDROID_SDK_ROOT"
sdkmanager --list_installed | grep -E 'platforms;android-36|build-tools;36.0.0|ndk;27.1.12516514|cmake;3.22.1'
```

## CI validation commands

```bash
python3 -m json.tool assets/manifest/asset_manifest.json
python3 tools/validate_asset_manifest.py assets/manifest/asset_manifest.json
python3 tools/validate_gameplay_data.py
python3 tools/build_asset_bundle.py --output build/GenesisProtocol_MetadataBundle_v01.tar.gz
python3 -m pytest tests/test_validate_asset_manifest.py tests/test_validate_gameplay_data.py
```
