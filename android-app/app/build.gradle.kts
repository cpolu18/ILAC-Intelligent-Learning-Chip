plugins {
    id("com.android.application")
}

android {
    namespace = "com.ilac.learningassistant"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.ilac.learningassistant"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

        ndk {
            abiFilters += "arm64-v8a"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation("org.pytorch:executorch-android:1.5.1")
}
