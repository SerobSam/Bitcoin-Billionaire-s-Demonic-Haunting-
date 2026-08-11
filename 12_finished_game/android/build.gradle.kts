plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.genesisprotocol.game"
    compileSdk = 36
    defaultConfig {
        applicationId = "com.genesisprotocol.game"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0.0"
        ndk { abiFilters += listOf("arm64-v8a") }
    }
    signingConfigs { create("release") { storeFile = file(System.getenv("GENESIS_KEYSTORE") ?: "release.keystore") } }
    buildTypes { release { isMinifyEnabled = true; isShrinkResources = true; signingConfig = signingConfigs.getByName("release") } }
    assetPacks += setOf(":assetpack_worlds", ":assetpack_audio", ":assetpack_highres")
}
