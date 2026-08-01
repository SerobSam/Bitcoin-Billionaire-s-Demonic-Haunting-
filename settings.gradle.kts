pluginManagement {
    repositories {
        gradlePluginPortal()
        google()
        mavenCentral()
    }
    resolutionStrategy {
        eachPlugin {
            when (requested.id.id) {
                "com.android.application" -> useModule("com.android.tools.build:gradle:9.3.0")
                "org.jetbrains.kotlin.android", "org.jetbrains.kotlin.jvm", "org.jetbrains.kotlin.plugin.serialization", "org.jetbrains.kotlin.kapt" -> useModule("org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.22")
                "com.google.devtools.ksp" -> useModule("com.google.devtools.ksp:com.google.devtools.ksp.gradle.plugin:1.9.22-1.0.14")
            }

        }
    }

}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
        maven { url = uri("https://jitpack.io") }
    }
}

rootProject.name = "Bitcoin-Billionaire-s-Demonic-Haunting-"
include(":app")
